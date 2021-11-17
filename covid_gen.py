import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb
from tabulate import tabulate
import os
from datetime import datetime, timedelta
from glob import glob
# our utilities will live here
from utils.utils import *
import progressbar

widgets = [' [combined.csv: ', 
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'), 
         '] ', 
           progressbar.Bar('*'),' (', 
           progressbar.ETA(), ') ', 
          ] 


# disable silly warning
pd.options.mode.chained_assignment = None  # default='warn'

# set up markdown summary generator
directory = Directory()
ddir = directory.ddir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

if not os.path.isdir(odir+'cleaned/withTimestamp/'):
  os.makedirs(odir+'cleaned/withTimestamp/')

HUGE = 10000000

# Get list of .csv files:

# setup markdown file output to report summary information
sfo = "covid_gen_summary.md"
sw = Summary(sfo)

# get the list of new files:
fdir = odir+"cleaned/withTimestamp/"

files = os.listdir(fdir)
frames = dict()
for fil in files:
  fi = fdir+fil
  # read raw .csv files 
  sw.wdv("Reading file:", fil)
  di = pd.read_csv(fi) # read file using pandas
  frames[fil] = di
  sw.wdv("Number of rows",di.shape[0])
  sw.wdv("Number of cols",di.shape[1])

  # TODO : Molly to add name standardization for each file
  #       e.g.   standard_names = Molly_Function(di["TEST"])
  # custom analysis for each file
  if(fil == 'combined.csv'):

    # stuff to look for:
    # patient summary information
    # number of records per patient
    # final discharge status?
    # patient timelines (

    print("Checking file: {}".format(fil))
    # identify pre and post encounters:
    di["ENCNTR"][di["HOSPITAL_DAY"] < 0] = -10  
    di["ENCNTR"][di["HOSPITAL_DAY"] > 999] = 1000  

    # start building training set
    # remove records that were "Unable to Calculate" or "See Note"
    #di = di[di["RESULT_VAL"] != "Unable to Calculate"]
    #di = di[di["RESULT_VAL"] != "See Note"]    
    # TODO : Add Timestamps to GroupBy
    # TODO : Add Vent Information
    #dft = di.drop_duplicates(subset=["RECORD_ID", "TEST", "ENCNTR", "DAYS_IN_ENCNTR", "VENT_FLAG", "VENT_DAY", "VENT_HOUR"], keep="first")#, "DAYS_IN_ENCNTR", "VENT_FLAG", "VENT_DAY", "VENT_TIME"]
    # TODO : Sort by RECORD_ID, then VERIFIED_DT, then VERIFIED_TM
    di.sort_values(by=['RECORD_ID', 'VERIFIED_DT', 'VERIFIED_TM'], inplace=True)
    # TODO : get "HOSPITAL_HOUR"
    #di["HOSPITAL_HOUR"] = np.array(di["VERIFIED_TM"].str[:2], dtype=float)+24*di["HOSPITAL_DAY"]
    #sw.wd("Computing HOSPITAL_HOUR : Noticed {} nan values".format(sum(np.isnan(di["HOSPITAL_HOUR"]))))

    fig = plt.figure()
    plt.hist(di["HOSPITAL_HOUR"], 100)
    plt.title("Histogram of \"HOSPITAL_HOUR\" in the data")
    plt.xlabel('HOSPITAL_HOUR in hours')

    fig.set_size_inches(24,12)

    fo = "img/HOSPITAL_HOUR_histogram.png"
    sw.wd("writing {}".format(fo))
    fig.savefig(fo, dpi=100)  
    sw.wi(fo)

    # read qualPts.csv and distinguish stays per patient
    fi = fdir+"qualPts.csv"
    dqp = pd.read_csv(fi) # read file using pandas
    dqp.sort_values(by=['RECORD_ID', 'CURRENT_REG_DT', 'CURRENT_REG_TM'], inplace=True)
    stay = np.ones(len(dqp))
    stay_dict = {}
    i = 0
    for row in dqp.iterrows():
      rid = row[1]["RECORD_ID"]
      if rid in stay_dict:
        stay_dict[rid]+=1
        stay[i] = stay_dict[rid]
      else:
        stay_dict[rid] = 1


      # TODO : for each row, lookup the records from di and label them
      #        with stay and other patient information
      i+=1
    sw.wd("qualPts.csv : found {}/{} RECORD_IDs with more than 1 stay".format(len(dqp["RECORD_ID"][stay>1].unique()), len(dqp["RECORD_ID"].unique())))

    sw.wd("drop any di records with nan \"HOSPITAL_HOUR\"")
    din = di[~np.isnan(di["HOSPITAL_HOUR"])]
    din["RESULT_VAL_num"] = pd.to_numeric(din["RESULT_VAL"], errors='coerce')
    din.sort_values(by=['RECORD_ID', "ENCNTR", "HOSPITAL_HOUR"], inplace=True)
    di_hour_min =  din[['RECORD_ID', "ENCNTR", "HOSPITAL_HOUR"]].drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep='first')
    di_hour_max =  din[['RECORD_ID', "ENCNTR", "HOSPITAL_HOUR"]].drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep='last')

    di_duration = pd.merge(di_hour_max, di_hour_min, how="left", on=["RECORD_ID", "ENCNTR"])
    di_duration["duration"] = di_duration.pop("HOSPITAL_HOUR_x") - di_duration.pop("HOSPITAL_HOUR_y")
    
    # TODO : check whether HOSPITAL_HOUR sorting ever conflicts with date and time

    disst_f = din[(din['TEST'].astype(str).str.contains('vent', case=False)) | (din['RESULT_VAL'].astype(str).str.contains('vent', case=False))].drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep='first')
    disst_f = disst_f[["RECORD_ID", "ENCNTR", "HOSPITAL_HOUR"]]
    disst_l = din[(din['TEST'].astype(str).str.contains('vent', case=False)) | (din['RESULT_VAL'].astype(str).str.contains('vent', case=False))].drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep='last')
    disst_l = disst_f[["RECORD_ID", "ENCNTR", "HOSPITAL_HOUR"]]
    sw.wd("{}/{} RECORD_IDs remain after dropping".format(len(din["RECORD_ID"].unique()), len(di["RECORD_ID"].unique())))
    # DONE : build grid (12 hrs?) for each patient over every hour they're in the hospital
    #        for each "RECORD_ID", "TEST", "HOSPITAL_HOUR" -- range from t_0 to t_n every 12hrs
    #        create a grid spot
    # take unique first and last records for each record_id
    dss_f = din.drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep="first")
    dss_l = din.drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep="last")

    # build default frame for 
    dso_base = din.drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep="first")
   
    # get rid of encounters before first admission and after last discharge...
    dso_base = dso_base[dso_base["ENCNTR"] < 999]
    dso_base = dso_base[dso_base["ENCNTR"] > -1]    
    # TODO : sort dso_base by RECORD_ID and ENCNTR
    # TODO : sort din by RECORD_ID, ENCNTR, VERIFIED_DT, and VERIFIED_TM

    # TODO : aggregate by record and encounter to see how many things happened in each encounter
    # TODO : aggregate by record, encounter, and test to see how much coverage there is for each test. 
    # TODO : make sure that intubated flag is "ON" whenever patient is intubated
    # TODO : make sure we keep a flag that says whether patient was intubated overall

    rid_strange = dqp
    # compose column of record_ids and column of hospital hours
    recs = np.array([])
    hours = np.array([])
    # loop through and build empty frame with everything -1
    tests = din["TEST"].unique()
    count = 0
    iii = 0

    
    # TODO : let this run for all record_ids at once
    # make list of times -- t_interval to np.ceil(maximum hospital hour)
    # loop through times -- filter out anything before this time. 
    #for index, row in dso_base.iterrows():

    #dis = din.loc[(din["RECORD_ID"] == row["RECORD_ID"]) &
    #              (din["ENCNTR"] == row["ENCNTR"])]
    #dis_f = dss_f.loc[(dss_f["RECORD_ID"] == row["RECORD_ID"]) &
    #              (dss_f["ENCNTR"] == row["ENCNTR"])]
    #dis_l = dss_l.loc[(dss_l["RECORD_ID"] == row["RECORD_ID"]) &
    #              (dss_l["ENCNTR"] == row["ENCNTR"])]
    t_interval = 4 # TODO : make this 4
    t_end = int(np.ceil(di["HOSPITAL_HOUR"].max()/t_interval)*t_interval)
    times = np.arange(t_interval, #int(dis_f["HOSPITAL_HOUR"]),
                      t_end+1,
                      t_interval)
    bar = progressbar.ProgressBar(max_value=int(len(times)),  
                                  widgets=widgets).start() 

    sw.wd("Generating Training Data for {} RECORD_IDs".format(len(dso_base)))
    #sw.wd("{} records, {} times in this encounter".format(len(dis), len(times)))
    if (len(times) < 1):
      sw.wd("Skipping because len(times) < 1")
    else:


      # for each time, drop duplicates from dis keeping most recent before time -- populate results for this row with those.
      for time in times:
        bar.update(iii)
        # fabricate blank dataframe
        # keys
        # RECORD_ID
        # ENCNTR
        # HOUR
        # filter to recordids which have hospital_hours from time-t_interval to time
        dins = din[(din["HOSPITAL_HOUR"] >  time-t_interval) &
                   (din["HOSPITAL_HOUR"] <= time)]
        # want to know if a patient has records after this time
        #dins["RESULT_VAL"] = dins["RESULT_VAL"].astype(float)

        # new base frame is drop duplicates by Record_ID and Encntr
        dins_further = din[(din["HOSPITAL_HOUR"] >  time-t_interval)]
        dinss = dins_further[["RECORD_ID", "ENCNTR"]]
        dsos = dinss.drop_duplicates(subset=["RECORD_ID", "ENCNTR"], keep="last")
        dsos["hour"] = time
        dsos = dsos.set_index(["RECORD_ID", "ENCNTR"])

        dsos_hr = dsos.copy()
        # compute time until vent:
        # "time" is our reference HOSPITAL_HOUR -- find earliest record of ventilation and subtract that hour from "time"
        if (len(disst_f) > 0):
          disst_f["time_until_vent"] = disst_f["HOSPITAL_HOUR"].astype(float)-time
          disst_fm = disst_f[["RECORD_ID", "ENCNTR", "time_until_vent"]]
          dsos = pd.merge(dsos, disst_fm, how="left", on=["RECORD_ID", "ENCNTR"])
        if (len(disst_l) > 0):
          disst_l["time_since_vent"] = time-disst_l["HOSPITAL_HOUR"].astype(float)
          disst_lm = disst_l[["RECORD_ID", "ENCNTR", "time_since_vent"]]
          dsos = pd.merge(dsos, disst_lm, how="left", on=["RECORD_ID", "ENCNTR"])        

        # fill na time util vent with HUGE
        dsos["time_until_vent"] = dsos["time_until_vent"].fillna(HUGE)#res["{}_x".format(col)])
        # fill na time since vent with -HUGE
        dsos["time_since_vent"] = dsos["time_since_vent"].fillna(-HUGE)#res["{}_x".format(col)])        


        # copying dataframe to get first and last entries
        dinscopy = dins.copy()
    
        # drop duplicates (last)
        diss = dins.drop_duplicates(subset=["RECORD_ID", "ENCNTR", "TEST"], keep="last")

        #  set the name of RESULT_VAL to test
        # now get the spread fields
        dissa = dins.groupby(["RECORD_ID", "ENCNTR", "TEST"]).mean()
        dissa.reset_index(inplace=True)
        #dissa.columns = ['RECORD_ID', 'ENCNTR', "{}-mean".format(test), '{}-mean-hour'.format(test)]
        #dissa.set_index(["RECORD_ID", "ENCNTR"])
        dinsam = dins[["RECORD_ID", "ENCNTR", "TEST", "RESULT_VAL_num", "HOSPITAL_HOUR"]]
        dissmin = dinsam.groupby(["RECORD_ID", "ENCNTR", "TEST"]).min()
        dissmin.reset_index(inplace=True)
        #dissmin.columns = ['RECORD_ID', 'ENCNTR', "{}-min".format(test), '{}-min-hour'.format(test)]
        #dissmin.set_index(["RECORD_ID", "ENCNTR"])
        dissmax = dinsam.groupby(["RECORD_ID", "ENCNTR", "TEST"]).max()
        dissmax.reset_index(inplace=True)
        #dissmax.columns = ['RECORD_ID', 'ENCNTR', "{}-max".format(test), '{}-max-hour'.format(test)]
        #dissmax.set_index(["RECORD_ID", "ENCNTR"])


        #for each test
        test_list = list()
        test_list = np.append(test_list, list(["time_until_vent"]))
        test_list = np.append(test_list, list(["time_since_vent"]))
        for test in tests:
          test_list = np.append(test_list, list([test]))
          test_list = np.append(test_list, list(["{}-hour".format(test)]))                    
          if (sum(diss["TEST"] == test) > 0):
            disss = diss[diss["TEST"] == test][["RECORD_ID", "ENCNTR", "RESULT_VAL", "HOSPITAL_HOUR"]]
            disss.columns = ['RECORD_ID', 'ENCNTR', test, '{}-hour'.format(test)]
            disss.set_index(["RECORD_ID", "ENCNTR"])
            #  join result to dsos
            dsos = pd.merge(dsos, disss, how="left", on=["RECORD_ID", "ENCNTR"])

        spread_fields = {"HR", "SBP", "DBP", "temp", "RR", "SpO2", "FiO2"}
        for field in spread_fields:
          testa = "{}-mean".format(field)
          testmin = "{}-min".format(field)
          testmax = "{}-max".format(field)
          test_list = np.append(test_list, list([testa]))
          test_list = np.append(test_list, list([testmin]))
          test_list = np.append(test_list, list([testmax]))

          if (sum(dissa["TEST"] == field) > 0):
            dissas = dissa[dissa["TEST"] == field][["RECORD_ID", "ENCNTR", "RESULT_VAL_num"]]
            dissas.columns = ['RECORD_ID', 'ENCNTR', testa]
            dissas.set_index(["RECORD_ID", "ENCNTR"])
            dsos = pd.merge(dsos, dissas, how="left", on=["RECORD_ID", "ENCNTR"])            

          if (sum(dissa["TEST"] == field) > 0):
            dissmins = dissmin[dissmin["TEST"] == field][["RECORD_ID", "ENCNTR", "RESULT_VAL_num"]]
            dissmins.columns = ['RECORD_ID', 'ENCNTR', testmin]
            dissmins.set_index(["RECORD_ID", "ENCNTR"])
            dsos = pd.merge(dsos, dissmins, how="left", on=["RECORD_ID", "ENCNTR"])            

          if (sum(dissa["TEST"] == field) > 0):
            dissmaxs = dissmax[dissmax["TEST"] == field][["RECORD_ID", "ENCNTR", "RESULT_VAL_num"]]
            dissmaxs.columns = ['RECORD_ID', 'ENCNTR', testmax]
            dissmaxs.set_index(["RECORD_ID", "ENCNTR"])
            dsos = pd.merge(dsos, dissmaxs, how="left", on=["RECORD_ID", "ENCNTR"])            


        #for metric in spread_metrics:
        #  test = "{}-{}".format(field, metric)
        #  if test in dsos.keys():
        #    dsos[test] = dsos[test].fillna(np.ones(dsos.shape[0]))#res["{}_x".format(test)])
        #  else:
        #    dsos[test] = -111.0

        # drop duplicates (first)
        diff = dinscopy.drop_duplicates(subset=["RECORD_ID", "ENCNTR", "TEST"], keep="first")
        
        #for each test
        init_test_list = list()
        for test in tests:
          init_test_list = np.append(init_test_list, list([str(test) + '_initial']))
          init_test_list = np.append(init_test_list, list(["{}-hour_initial".format(test)]))                    
          if (sum(diff["TEST"] == test) > 0):
            difff = diff[diff["TEST"] == test][["RECORD_ID", "ENCNTR", "RESULT_VAL", "HOSPITAL_HOUR"]]
            difff.columns = ['RECORD_ID', 'ENCNTR', str(test) + '_initial', '{}-hour_initial'.format(test)]
            difff.set_index(["RECORD_ID", "ENCNTR"])
            #  join result to dsos
            dsos = pd.merge(dsos, difff, how="left", on=["RECORD_ID", "ENCNTR"])
            
        # for each unique test, fill in -1.0s for values
        # do this at the very end to fill in nas
        # 0x0011a08b
        alltests = np.append(test_list.copy(), init_test_list)
        test_list = np.append(["RECORD_ID",  "ENCNTR",  "hour"], alltests, )
        for col in test_list:
          if col in dsos.keys():
            dsos[col] = dsos[col].fillna(-111.0)#res["{}_x".format(col)])
          else:
            dsos[col] = -111.0

        if (iii < 1):
          # use dsos to create the output frame
          dsot = dsos[test_list]

          fo = odir+"covid_gen_all_along-{}.csv".format(t_interval)
          dsos[test_list].to_csv(fo, mode='w', header=True, sep=",", index=False)

        else:
          # append this as a new row
          fo = odir+"covid_gen_all_along-{}.csv".format(t_interval)
          dsos[test_list].to_csv(fo, mode='a', header=False, sep=",", index=False)

          dsot = dsot.append(dsos[test_list])

        #fo = odir+"covid_gen_along-{}.csv".format(t_interval)
        #hdr = False  if os.path.isfile(fo) else True
        #dsos.to_csv(fo, mode='a', header=hdr, sep=",")

        #fo = odir+"covid_gen_along-{}-Hour.csv".format(t_interval)
        #hdr = False  if os.path.isfile(fo) else True
        #dsos_hr.to_csv(fo, mode='a', header=hdr, sep=",")

        iii+=1
    count+=1    
    #        between min and max
    #        for each grid hour, take the subset of the tests less
    #            than that hour and join it with the new table
    #            we'll take the RESULT_VAL of the latest HOSPITAL_HOUR
    #            we'll also write down the sampled HOSPITAL_HOUR
    # create index
    # TODO : Add "DECEASED_FLAG" from qualPts.csv
    # if SpO2 and FiO2 both exist, compute ratio and add that
    
    
    if ("SpO2" in dsot) & ("FiO2" in dsot):
      subset = (dsot["SpO2"].astype(float) > 0) & (dsot["FiO2"].astype(float) > 0)

      if sum(subset) > 0:
        sw.wd("Computing SpO2/FiO2 : {}/{}".format(subset.sum(), len(subset)))
        spofi = dsot["SpO2"][subset].astype(float)/dsot["FiO2"][subset].astype(float)
        spofit = (-111.0)*(np.ones(dsot.shape[0]))
        spofit[subset] = spofi
        dsot["SpO2/FiO2"] = spofit

    fo = odir+"covid_gen_all-{}.csv".format(t_interval)
    dsot = pd.merge(dsot, di_duration, how="left", on=["RECORD_ID", "ENCNTR"])
    dsot.to_csv(fo, sep=",", index=False)

  elif(fil == 'clinicalEvents.csv'):
      print('Checking file: {}'.format(fil))
  elif(fil == 'diagnosisHx.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'labs.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'locationHx.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'meds.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'pregnantPts.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'qualPts.csv'):
    print("Checking file: {}".format(fil))
  elif(fil == 'vent.csv'):
    # find out whether patients got intubated later so we can label
    #     the training set.
    
    print("Checking file: {}".format(fil))
  elif(fil == 'vitals.csv'):
    print("Checking file: {}".format(fil))


