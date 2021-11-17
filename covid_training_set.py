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

widgets = [' [ClinicalEvents.csv: ', 
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

t_interval = 4 # TODO : make this 4

# set up summary
sfo = "covid_gen_summary.md"
sw = Summary(sfo)

# read covid_gen
fi = odir+"covid_gen_all-{}_fillna.csv".format(t_interval)
di = pd.read_csv(fi)
# make sure we're sorted by
di.sort_values(by=["RECORD_ID", "ENCNTR", "hour"], inplace=True)
# fillna
training_fields = np.array([])
for col in di.keys():
  # convert -111.0 to NA
  di[col][di[col] == -111.0] = np.NaN
  di[col] = di[col].fillna(method='ffill', limit=4)
  sw.wd("{} \t: {} non null values".format(col, sum(pd.notnull(di[col]))))
  if sum(pd.notnull(di[col])) > .15*di.shape[0]:
    training_fields = np.append(training_fields, [col])
  
# define positive and negative casees -- label rows


#di["72hr_vent"] = 0
#di["72hr_vent"][(di["time_until_vent"] < 72) & (di["time_until_vent"] >= 0)] = 1
#di["72hr_vent"][di["time_until_vent"] < 0] = 2
#training_fields = np.append(training_fields, ["72hr_vent"])

fi = odir+"ColumnInfo.csv"
cinfo = ColumnInfo(fi)
cinfo_d = cinfo.GetFrame()
#cinfo_d["subset"] = cinfo_d["contains_string"] + cinfo_d["training_spoiler"] + cinfo_d["hour"]
cinfo_d["subset"] = cinfo_d["contains_string"] + cinfo_d["training_spoiler"] + cinfo_d["hour"]

# intersect the training fields with non-strings, non-spoilers, and non-hours
training_fields = list(set(training_fields) & set(list(cinfo_d["columns"][cinfo_d["subset"] < 1])))
# move non-predictors to front
training_fields.insert(0, training_fields.pop(training_fields.index('time_since_vent')))
training_fields.insert(0, training_fields.pop(training_fields.index('time_until_vent')))
training_fields.insert(0, training_fields.pop(training_fields.index('duration')))
training_fields.insert(0, training_fields.pop(training_fields.index('hour')))
training_fields.insert(0, training_fields.pop(training_fields.index('ENCNTR')))
training_fields.insert(0, training_fields.pop(training_fields.index('RECORD_ID')))

# filter down to training fields
dio = di[training_fields]
# filter out bad(?) rows
# for each column eliminate rows missing values for this column


fi = odir+"/cleaned/WithTimeStamp/qualPts.csv"
dqp = pd.read_csv(fi) # read file using pandas
dqp = dqp.drop_duplicates(subset=["RECORD_ID"], keep="last")
dqp = dqp[["RECORD_ID", "PATIENT_AGE","SEX"]]
# convert "> 89" to 90
dqp["PATIENT_AGE"][dqp["PATIENT_AGE"] == "> 89"] = 90
dqp["PATIENT_AGE"] = pd.to_numeric(dqp["PATIENT_AGE"])
#dqp.sort_values(by=['RECORD_ID', 'CURRENT_REG_DT', 'CURRENT_REG_TM'], inplace=True)

#Converting Sex values (1 -> Male, 2-> Female)
dqp['SEX'][dqp['SEX'] == 'Male'] = 1
dqp['SEX'][dqp['SEX'] == 'Female'] = 2
#print(pd.unique(dqp['SEX']))

#dsos = pd.merge(dsos, disst_fm, how="left", on=["RECORD_ID", "ENCNTR"])
dio = pd.merge(dio, dqp, how="left", on=["RECORD_ID"])

thresholds = [10,50]
for threshold in thresholds:
    #diot = removerows(dio, threshold, False)
    diot = dio.replace([111.0,'-111.0',111,'111',-111.],np.nan)
    rowcount = diot.count(axis = 'columns')
    
    newidx = rowcount[rowcount >= threshold]
    
    diot = diot.iloc[list(newidx.index)]
    diot = diot.set_index(pd.RangeIndex(start = 0, stop = len(diot.index), step = 1))
    
    diot = diot.fillna(-111.0)
    
    # fill any remaining na with 0.0
    #diot = dio.fillna(0.0)
    
    # write covid_train.csv
    fo = odir+"covid_training_set-{}_{}.csv".format(t_interval, threshold)
    sw.wd("Writing {}".format(fo))
    sw.wd("with fields: {}".format(diot.columns))
    diot.to_csv(fo, sep=",", index=False)
