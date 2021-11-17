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

# Get list of .csv files:

# setup markdown file output to report summary information
sfo = "covid_clean_summary.md"
sw = Summary(sfo)

# covid_clean : description
sw.wd("This workflow reads the combined datafile and produces a cleaned file that can be used to generate training data. Operations include converting column names, cleaning up stray strings in numeric data, etc...")

# Reading in combined file
fdir = ddir+"/withTimestamp/csv/"
fil = 'combined.csv'
di = pd.read_csv(fdir + fil)

sw.wdv("Reading file:", fil)
sw.wdv("Number of rows",di.shape[0])
sw.wdv("Number of cols",di.shape[1])

do = di

# clean alternate fio2
fio2 = do.loc[do['TEST']=='FIO2, Arterial POC','RESULT_VAL']
col, rep = clean_fio2_col(fio2, sw)
do.loc[do['TEST']=='FIO2, Arterial POC','RESULT_VAL'] = col
# TODO : document what's happening here!
sw.wd("FIO2 : {} records, cleaning {} values ".format(len(fio2), len(rep)))
# TODO : How many changes were made?

# clean ratios
ratio_tests = ['Inspiratory to Expiratory Ratio','Inspiratory to Expiratory Ratio Measured']
for test in ratio_tests:
  old_col = do.loc[do['TEST']==test,'RESULT_VAL']
  col,rep = clean_ratio_col(old_col, sw)
  sw.wd("Ratio Test {} : {} records, cleaning {}".format(test, len(old_col), len(col)))
  do.loc[do['TEST']==test,'RESULT_VAL']=col

# clean positive/negative
posneg_tests = ['Coronavirus (COVID-19) SARS-CoV-2 RNA', 'Bilirubin, UR',
               'Coronavirus(COVID-19)SARS CoV2 TL Result']
for test in posneg_tests:
  old_col = do.loc[do['TEST']==test,'RESULT_VAL']
  col,rep = clean_posneg_col(old_col, sw)
  sw.wd("PosNeg Test {}: {} records, cleaning {}".format(test, len(old_col), len(col)))      
  do.loc[do['TEST']==test,'RESULT_VAL']=col

# relabel O2
old_col = do.loc[do['TEST']=='Oxygen Therapy','RESULT_VAL']
new_col = relabelO2(old_col, sw)
sw.wd("O2: {} records, cleaning {}".format(len(old_col), len(col)))    
do.loc[do['TEST']=='Oxygen Therapy','RESULT_VAL'] = new_col

# clean gcs
for test in ['Glasgow Coma Score','ED Document Glasgow Coma Scale']:
  old_col = do.loc[do['TEST']==test,'RESULT_VAL']
  col, rep = clean_gcs_col(old_col, sw)
  sw.wd("{}: {} records, cleaning {}".format(test, len(old_col), len(col)))      
  do.loc[do['TEST']==test,'RESULT_VAL']=col

# clean leftover strings
clean_tests = ['Chloride', 'Respiratory Rate', 'Glucose Level',
               'Systolic Blood Pressure', 'Height (in)', 'SpO2', 'BUN',
               'Diastolic Blood Pressure', 'Heart Rate Monitored', 'Creatinine', 'Weight',
               'BUN/Creat Ratio', 'Height', 'Calcium', 'Temperature (F)',
               'Weight (lb)', 'WBC', 'BMI (Pt Care)', 'RBC', 'Heart Rate EKG', 'HGB',
               'HCT', 'MCH', 'MCHC', 'MCV', 'RDW-CV', 'Platelet', 'MPV',
               'Lymphocytes %', 'Bilirubin Total', 'NT-proBNP', 'Lymphocytes #', 'D-Dimer, Quant',
               'C Reactive Protein', 'Ferritin', 'O2 Sat, ABG POC', 'RDW-SD', 'FIO2', 'D-Dimer Quantitative',
               'eGFR (non-African Descent)', 'Ferritin Level', 'Cholesterol', 'Troponin-T, High Sensitivity',
               'Troponin T, High Sensitivity', 'SBP', 'Cholesterol/HDL Ratio', 'DBP', 'Bilirubin  Direct',
               'Height Calculation', 'Non HDL Cholesterol', 'Inspiratory Time', 'Transcribed Height (cm)',
               'CRP High Sens', 'MSOFA Score', 'FIO2, Arterial POC', 'PEEP.', 'PCO2, ABG POC',
               'HCO3(Bicarb), ABG POC', 'Peak Inspiratory Pressure',
               'Ventilator Frequency, Mandatory',
               'Positive End Expiratory Pressure', 'Auto-PEEP',
               'End Expiratory Pressure', 'Inspiratory Flow Rate', 'Bilirubin Direct Serum',
               'Inspiratory Pressure', 'Interleukin-2 (IL-2)',
               'Interleukin-2 (IL-2) (RL)']

for test in clean_tests:
  old_col = do.loc[do['TEST']==test,'RESULT_VAL']
  sw.wd("Checking for suspect records in {}".format(test))
  col, rep = clean_col(old_col, sw)
  do.loc[do['TEST']==test,'RESULT_VAL'] = col
  
# Clean test names
sw.wd("Relabeling Tests")
do = relabelTests_ce(do)

# Clean lab names
sw.wd("Relabeling Labs")
do = relabelLabs_labs(do)
do = do[~do.TEST.isin(irrelevantTests)]

# clean glucose values
glucose = pd.to_numeric(do.loc[do['TEST']=='glucose','RESULT_VAL'],errors='coerce')
do.loc[do['TEST']=='glucose','RESULT_VAL'] = glucose

# Labeling encounters
sw.wd("Identifying Encounters")
do = identify_encntrs(do, sw)

# Identifying patients who were ventilated
sw.wd("Identifying Vent")
do = identify_vent(do, sw)

# Exporting Cleaned combined.csv
fo = odir+"cleaned/withTimestamp/"+fil
do.to_csv(fo,index=False)
