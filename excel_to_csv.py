import numpy as np
import pandas as pd
from datetime import datetime, date
import progressbar

widgets = [' [', 
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'), 
         '] ', 
           progressbar.Bar('*'),' (', 
           progressbar.ETA(), ') ', 
          ] 
  
from utils.utils import *


## Script to read excel and save CSV's (slightly altered)
directory = Directory()
ddir = directory.ddir + 'withTimestamp/'

# clinical events
print('Reading clinical events sheet')
# ce = pd.read_excel(ddir+'DOUGLAS - COVID_10092020.xlsx',sheet_name='CLINICAL_EVENTS', engine="openpyxl")
ce = pd.read_excel(ddir+'DOUGLAS - COVID_10092020.xlsx',sheet_name='CLINICAL_EVENTS', engine="openpyxl", parse_dates=False)
ce=renamecols(ce)

# qualPts
print('Reading qualpts sheet')
qp = pd.read_excel(ddir+'DOUGLAS - COVID_10092020.xlsx',sheet_name='QUALIFYING_PTS', engine="openpyxl", parse_dates=False)
print('read qp')

## add hospital_day col to clinical events using values in qualPt
ce['HOSPITAL_DAY'] = np.nan
ce['HOSPITAL_HOUR'] = np.nan
ce['ENCOUNTER_DAY'] = np.nan
ce['ENCOUNTER_HOUR'] = np.nan
ce['ADMISSION_DateTime'] = np.nan

bar = progressbar.ProgressBar(max_value=len(ce),  
                              widgets=widgets).start() 

print('Adding hospital/encounter day, hospital/encounter hour')
for idx, row in ce.iterrows():
    ## print progress
    if idx % 20 == 0:
      bar.update(idx)
    if idx % 20000 == 0 and idx > 1:
        print(f'Row {idx} of {ce.shape[0]}')

    ## if we don't have a test time, skip
    if pd.isnull(row['VERIFIED_DT']):
        continue

    ## find qualpts rows that match this patient
    rid = row['RECORD_ID']
    qp_rows = qp.loc[qp['RECORD_ID']==rid]

    ## find minimum datetime
    admit_dates = qp_rows['CURRENT_REG_DT'].dt.to_pydatetime()
    admit_times = list(qp_rows['CURRENT_REG_TM'])
    for i in range(len(admit_times)):
      if type(admit_times[i]) == datetime:
        admit_times[i] = admit_times[i].time()
      
    #if type(admit_times[0]) == datetime:
    #    print('Found datetime where a time should be. this will likely cause issues. Check if youre using the new openpyxl engine for read_csv. Might need to change things to be compatible with that')
    # admit_times[type(admit_times[0]) == datetime] =  admit_times[type(admit_times[0]) == datetime].time()
    admit_datetimes = [datetime.combine(d, t) for d, t in zip(admit_dates,admit_times)]
    admit_1 = np.min(admit_datetimes)

    ## find datetime of test
    test_date = row['VERIFIED_DT'].to_pydatetime()
    test_time = row['VERIFIED_TM']
    if type(test_time) == datetime:
      test_time = test_time.time()

    test_dt = datetime.combine(test_date,test_time)

    ## fill in hospital date and time
    hospital_td = test_dt - admit_1
    ce.iloc[idx, ce.columns.get_loc('HOSPITAL_DAY')] = hospital_td.days
    ce.iloc[idx, ce.columns.get_loc('HOSPITAL_HOUR')] = hospital_td.total_seconds() / 3600

    ## loop through qualpts rows sorted by date and time
    row_ct = 0
    before_discharges = []
    after_admissions = []
    for j, qp_row in qp_rows.sort_values(['CURRENT_REG_DT','CURRENT_REG_TM'],ascending=False).iterrows():
        row_ct += 1
        ## find time difference between admission and test
        encntr_date = qp_row['CURRENT_REG_DT'].to_pydatetime()
        encntr_time = qp_row['CURRENT_REG_TM']
        if type(encntr_time) == datetime:
          encntr_time = encntr_time.time()
        encntr_dt = datetime.combine(encntr_date,encntr_time)
        td = test_dt - encntr_dt
        # ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_DAY')] = td.days
        # ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_HOUR')] = td.total_seconds() / 3600

        # after_admission = td.total_seconds() >= 0
            
        ## check if test happened before discharge, if there is one
        #if pd.isnull(qp_row['CURRENT_DISCH_DT']):
        #    before_discharge = True
        #else:
        #    disch_date = qp_row['CURRENT_DISCH_DT']
        #    disch_time = qp_row['CURRENT_DISCH_TM']
        #    disch_dt = datetime.combine(disch_date,disch_time)
        #    before_discharge = disch_dt >= test_dt

        ## keep track if we find a suitable encounter
        # before_discharges += [int(before_discharge)]
        # after_admissions += [int(after_admission)]
            
        ## if the time fits, calculate hospital day, time



        # if test is  after_admission:
        if td.total_seconds() >= 0:
            ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_DAY')] = td.days
            ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_HOUR')] = td.total_seconds() / 3600
            ce.iloc[idx, ce.columns.get_loc('ADMISSION_DateTime')] = encntr_dt
            break
            
        # if we got to the end and nothing worked fill in negatives
        if row_ct == qp_rows.shape[0] and td.total_seconds() < 0:
            ## if before all admissions, give negative time relative to 1st
            ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_DAY')] = hospital_td.days
            ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_HOUR')] = hospital_td.total_seconds() / 3600
            ce.iloc[idx, ce.columns.get_loc('ADMISSION_DateTime')] = admit_1
            

            #if sum(before_discharges) + sum(after_admissions) == 0:
            #    print('1')
            #    pdb.set_trace()
                ## if before all admissions and after all discharges, investigate
            #    print('Examine this row')
                #print(row)
            #elif sum(before_discharges) == 0 :
                ## if after all discharges, say so
            #    ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_DAY')] = 1000
            #    ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_HOUR')] = 24000
            #elif sum(after_admissions) == 0:
                ## if before all admissions, give negative time relative to 1st
            #    ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_DAY')] = hospital_td.days
            #    ce.iloc[idx, ce.columns.get_loc('ENCOUNTER_HOUR')] = hospital_td.total_seconds() / 3600
            #else:
            #    print('2')
            #    pdb.set_trace()
                ## not sure this is possible but just in case
            #    print('Examine this row:')
                #print(row)

print('saving clinical events, qualifying patients')
ce.to_csv(ddir+'csv/clinicalEvents.csv',index=False)
qp.to_csv(ddir+'csv/qualPts.csv',index=False)
ce = None # delete from memory to save space? I think should help in theory        

# labs
print('reading labs sheet')
# lb1 = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='LABS', engine="openpyxl")
# lb2 = pd.read_excel(ddir+'Douglas-MoreGoodLabs_12122020.xlsx', engine="openpyxl")
lb1 = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='LABS', engine="openpyxl", parse_dates=False)
lb2 = pd.read_excel(ddir+'Douglas-MoreGoodLabs_12122020.xlsx', engine="openpyxl", parse_dates=False)
lb = pd.concat([lb1,lb2], ignore_index=True)

## add hospital_day col to clinical events using values in qualPt
lb['HOSPITAL_DAY'] = np.nan
lb['HOSPITAL_HOUR'] = np.nan
lb['ENCOUNTER_DAY'] = np.nan
lb['ENCOUNTER_HOUR'] = np.nan
lb['ADMISSION_DateTime'] = np.nan

bar = progressbar.ProgressBar(max_value=len(lb),  
                              widgets=widgets).start() 

print('Adding hospital/encounter day, hospital/encounter hour')
for idx, row in lb.iterrows():
    ## print progress
    if idx % 20 == 0:
      bar.update(idx)
    if idx % 20000 == 0 and idx > 1:
        print(f'Row {idx} of {lb.shape[0]}')

    ## if we don't have a test time, skip
    if pd.isnull(row['TEST_DT']):
        continue

    ## find qualpts rows that match this patient
    rid = row['PERSON_ID']
    qp_rows = qp.loc[qp['RECORD_ID']==rid]

    if qp_rows.shape[0] == 0:
        print(f'\nid {rid} not found in qual pts\n')
        continue

    ## find minimum datetime
    admit_dates = qp_rows['CURRENT_REG_DT'].dt.to_pydatetime()
    admit_times = list(qp_rows['CURRENT_REG_TM'])
    if type(admit_times[0]) == datetime:
        print('Found datetime where a time should be. this will likely cause issues. Check if youre using the new openpyxl engine for read_csv. Might need to change things to be compatible with that')
    # admit_times[type(admit_times[0]) == datetime] =  admit_times[type(admit_times[0]) == datetime].time()
    admit_datetimes = [datetime.combine(d, t) for d, t in zip(admit_dates,admit_times)]
    admit_1 = np.min(admit_datetimes)

    ## find datetime of test
    test_date = row['TEST_DT'].to_pydatetime()
    test_time = row['TEST_TM']
    if type(test_time) is str:
        test_time = datetime.strptime(test_time, '%H:%M:%S.%f').time()
    test_dt = datetime.combine(test_date,test_time)

    ## fill in hospital date and time
    hospital_td = test_dt - admit_1
    lb.iloc[idx, lb.columns.get_loc('HOSPITAL_DAY')] = hospital_td.days
    lb.iloc[idx, lb.columns.get_loc('HOSPITAL_HOUR')] = hospital_td.total_seconds() / 3600

    ## loop through qualpts rows sorted by date and time
    row_ct = 0
    before_discharges = []
    after_admissions = []
    for j, qp_row in qp_rows.sort_values(['CURRENT_REG_DT','CURRENT_REG_TM'],ascending=False).iterrows():
        row_ct += 1

        ## find time difference between admission and test
        encntr_date = qp_row['CURRENT_REG_DT'].to_pydatetime()
        encntr_time = qp_row['CURRENT_REG_TM']
        encntr_dt = datetime.combine(encntr_date,encntr_time)
        td = test_dt - encntr_dt
            
        ## if the time fits, calculate hospital day, time
        # if test is  after_admission:
        if td.total_seconds() >= 0:
            lb.iloc[idx, lb.columns.get_loc('ENCOUNTER_DAY')] = td.days
            lb.iloc[idx, lb.columns.get_loc('ENCOUNTER_HOUR')] = td.total_seconds() / 3600
            lb.iloc[idx, lb.columns.get_loc('ADMISSION_DateTime')] = encntr_dt
            break
            
        # if we got to the end and nothing worked fill in negatives
        if row_ct == qp_rows.shape[0] and td.total_seconds() < 0:
            ## if before all admissions, give negative time relative to 1st
            lb.iloc[idx, lb.columns.get_loc('ENCOUNTER_DAY')] = hospital_td.days
            lb.iloc[idx, lb.columns.get_loc('ENCOUNTER_HOUR')] = hospital_td.total_seconds() / 3600
            lb.iloc[idx, lb.columns.get_loc('ADMISSION_DateTime')] = admit_1

            
print('saving labs')
lb.to_csv(ddir+'csv/labs.csv',index=False)
lb = None
lb1 = None
lb2 = None

# vitals
print('reading vitals sheet')
#vi = pd.read_excel(ddir+'DOUGLAS - COVID_10092020.xlsx',sheet_name='VITALS', engine="openpyxl")
vi = pd.read_excel(ddir+'DOUGLAS - COVID_10092020.xlsx',sheet_name='VITALS', engine="openpyxl", parse_dates=False)
print('read vitals sheet')

# rename some columns for common keys
mapper = {'HRT_RT_DT':'HEART_RT_DT',
         'HRT_RT_TM':'HEART_RT_TM',
         'RESP_RATE':'RESP_RT',
         'BP_DIASTOLIC':'BP_DIA',
         'BP_SYSTOLIC':'BP_SYS'}
vi = vi.rename(columns=mapper)

# create common df for output
out_cols = ['RECORD_ID','RESULT','UNITS','DT','TM','VITAL']
df = pd.DataFrame(columns=out_cols)
vitals = ['HEIGHT','WEIGHT','HEART_RT','RESP_RT','BP_DIA','BP_SYS']
for v in vitals:
    # find all cols of this type
    idx = [v in col for col in vi.columns]
    idx[0] = True
    tmp = vi[vi.columns[idx]]
    
    # reshape into our output
    tmp['VITAL'] = v
    tmp.columns = ['RECORD_ID','RESULT','UNITS','DT','TM','VITAL']
    
    # combine with others
    df = pd.concat([df,tmp],ignore_index=True)
vi = df

## add hospital_day col to clinical events using values in qualPt
vi['HOSPITAL_DAY'] = np.nan
vi['HOSPITAL_HOUR'] = np.nan
vi['ENCOUNTER_DAY'] = np.nan
vi['ENCOUNTER_HOUR'] = np.nan
vi['ADMISSION_DateTime'] = np.nan

bar = progressbar.ProgressBar(max_value=len(vi),  
                              widgets=widgets).start() 

print('Adding hospital/encounter day, hospital/encounter hour')
for idx, row in vi.iterrows():
    ## print progress
    if idx % 20 == 0:
      bar.update(idx)
    if idx % 20000 == 0 and idx > 1:
        print(f'Row {idx} of {vi.shape[0]}')

    ## if we don't have a test time, skip
    if pd.isnull(row['DT']):
        continue

    ## find qualpts rows that match this patient
    rid = row['RECORD_ID']
    qp_rows = qp.loc[qp['RECORD_ID']==rid]

    ## find minimum datetime
    admit_dates = qp_rows['CURRENT_REG_DT'].dt.to_pydatetime()
    admit_times = list(qp_rows['CURRENT_REG_TM'])
    if type(admit_times[0]) == datetime:
        print('Found datetime where a time should be. this will likely cause issues. Check if youre using the new openpyxl engine for read_csv. Might need to change things to be compatible with that')
    # admit_times[type(admit_times[0]) == datetime] =  admit_times[type(admit_times[0]) == datetime].time()
    admit_datetimes = [datetime.combine(d, t) for d, t in zip(admit_dates,admit_times)]
    admit_1 = np.min(admit_datetimes)

    ## find datetime of test
    test_date = row['DT'].to_pydatetime()
    test_time = row['TM']
    test_dt = datetime.combine(test_date,test_time)

    ## fill in hospital date and time
    hospital_td = test_dt - admit_1
    vi.iloc[idx, vi.columns.get_loc('HOSPITAL_DAY')] = hospital_td.days
    vi.iloc[idx, vi.columns.get_loc('HOSPITAL_HOUR')] = hospital_td.total_seconds() / 3600

    ## loop through qualpts rows sorted by date and time
    row_ct = 0
    before_discharges = []
    after_admissions = []
    for j, qp_row in qp_rows.sort_values(['CURRENT_REG_DT','CURRENT_REG_TM'],ascending=False).iterrows():
        row_ct += 1

        ## find time difference between admission and test
        encntr_date = qp_row['CURRENT_REG_DT'].to_pydatetime()
        encntr_time = qp_row['CURRENT_REG_TM']
        encntr_dt = datetime.combine(encntr_date,encntr_time)
        td = test_dt - encntr_dt
            
        ## if the time fits, calculate hospital day, time
        # if test is  after_admission:
        if td.total_seconds() >= 0:
            vi.iloc[idx, vi.columns.get_loc('ENCOUNTER_DAY')] = td.days
            vi.iloc[idx, vi.columns.get_loc('ENCOUNTER_HOUR')] = td.total_seconds() / 3600
            vi.iloc[idx, vi.columns.get_loc('ADMISSION_DateTime')] = encntr_dt
            break
            
        # if we got to the end and nothing worked fill in negatives
        if row_ct == qp_rows.shape[0] and td.total_seconds() < 0:
            ## if before all admissions, give negative time relative to 1st
            vi.iloc[idx, vi.columns.get_loc('ENCOUNTER_DAY')] = hospital_td.days
            vi.iloc[idx, vi.columns.get_loc('ENCOUNTER_HOUR')] = hospital_td.total_seconds() / 3600
            vi.iloc[idx, vi.columns.get_loc('ADMISSION_DateTime')] = admit_1
            
print('saving vitals sheet')
vi.to_csv(ddir+'csv/vitals.csv',index=False)
vi = None # delete from memory to save space? I think should help in theory

# medication history
print('reading medication history')
# mh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='MEDICATION_HISTORY', engine="openpyxl")
mh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='MEDICATION_HISTORY', engine="openpyxl", parse_dates=False)
print('saving medication history')
mh.to_csv(ddir+'csv/medication_history.csv',index=False)
mh = None

# pregnant pts
print('reading pregnant patients')
# pp = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='PREGNANT_PTS', engine="openpyxl")
pp = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='PREGNANT_PTS', engine="openpyxl", parse_dates=False)
print('saving pregnant patients')
pp.to_csv(ddir+'csv/pregnant_pts.csv',index=False)
pp = None

# diagnosis history
print('reading diagnosis history')
#dh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='DIAGNOSIS_HISTORY', engine="openpyxl")
dh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='DIAGNOSIS_HISTORY', engine="openpyxl", parse_dates=False)
print('saving diagnosis history')
dh.to_csv(ddir+'csv/diagnosis_history.csv',index=False)
dh = None

# location history
print('reading location history')
# lh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='LOCATION_HISTORY', engine="openpyxl")
lh = pd.read_excel(ddir+'DOUGLAS - COVID_11062020.xlsx',sheet_name='LOCATION_HISTORY', engine="openpyxl", parse_dates=False)
print('saving location history')
lh.to_csv(ddir+'csv/location_history.csv',index=False)
lh = None
