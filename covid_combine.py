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

# Get list of .csv files:

# setup markdown file output to report summary information
sfo = "covid_combine_summary.md"
sw = Summary(sfo)

# covid_clean : description
sw.wd("This workflow reads and combines clinicalevents, labs, and vitals")

# get the list of new csv files:
fdir = ddir+"withTimestamp/csv/"
files = glob(fdir+'*.csv')    

frames = dict()

comb = pd.DataFrame()
for filepath in files:
    sw.wd("reading file: {}".format(filepath))
    filepath = filepath.replace("\\","/")
    fil = filepath.split('/')[-1]
    di = pd.read_csv(filepath)#, encoding='latin-1') # read file using pandas
    
    frames[fil] = di
    sw.wdv("Reading file:", fil)
    sw.wdv("Number of rows",di.shape[0])
    sw.wdv("Number of cols",di.shape[1])
    
    if(fil == 'clinicalEvents.csv'):
        sw.wd('Adding clinical events to combined file.')

        sw.wd("Cleaning file: {}".format(fil))
        di = renamecols(di)
        comb = pd.concat([comb,di], axis = 0)
    
    elif(fil == 'labs.csv'):
        sw.wd('Adding labs to combined file.')
        
        di = renamecols(di)
        comb = pd.concat([comb,di], axis = 0)
    
    elif(fil == 'vitals.csv'):
        sw.wd('Adding vitals to combined file.')

        di = renamecols(di)
        comb = pd.concat([comb,di], axis = 0)

# Saving New CSV
fo = ddir +"withTimestamp/csv/combined.csv"
comb.to_csv(fo, index=False)