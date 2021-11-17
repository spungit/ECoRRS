import pandas as pd
import numpy as np
from tabulate import tabulate
import os
import sys
from datetime import datetime, timedelta
import re
import json
import pdb
import matplotlib.pyplot as plt
from scipy.stats import ksone

# summary.md generator
class Summary(object):
  def __init__(self, fo):
    self.fo = fo
    self.first = True
  # TODO : convert if statements and printing to generic function
  # TODO : have each summary function call generic print function
  # write description to covid_summary.md
  def summary_print(self, desc):
    print("{}\n".format(desc))
    if (self.first):
      print("{}\n".format(desc), file=open(self.fo,"w"))
      self.first = False
    else:
      print("{}\n".format(desc), file=open(self.fo,"a"))

  def wd(self, desc):
    descr = "## {}".format(desc)
    self.summary_print(descr)
  # write title to covid_summary.md
  def wt(self, desc):
    descr = "# {}".format(desc)
    self.summary_print(descr)
  # write description with value to covid_summary.md
  def wdv (self, desc, data):
    descr = "### {} : {}".format(desc, data)
    self.summary_print(descr)
  def wi (self, fo):
    #url = "https://github.com/bwbellmath/patient_trajectories/blob/b2_updates-2020-11-03/"
    descr = "### Included Image: {}".format(fo)
    self.summary_print(descr)
    #descr_image = "![{}]({}{})".format(fo, url, fo)
    descr_image = "![{}]({})".format(fo, fo)
    self.summary_print(descr_image)

# Add Beamer generator
class Beamer(object):
  def __init__(self,out_name,out_dir='./',title='',author=''):
    self.title = title
    self.author = author

    self.out_dir = out_dir
    self.out_name = out_name
    self.out_path = os.path.join(out_dir,out_name)
    # make out_dir only if it doesn't exist yet
    if not os.path.isdir(out_dir):
      os.makedirs(out_dir)

    # preamble
    self.text = '\\documentclass{beamer}\n\\usepackage{graphics}\n'
    self.text += '\\usetheme{Montpellier}\n'
    self.text += '\\usepackage[utf8]{inputenc}\n\\title{'+self.title+'}\n\\author{'+self.author+'}\n'
    self.text += '\\institute{University of Arizona}\n\\date{\\today}\n\n\\begin{document}\n'
    self.text += '\\titlepage{}\n'

  # function to start new frame
  def new_frame(self):
    self.text += '\\begin{frame}\n'

  # function to end frame
  def end_frame(self):
    self.text += '\\end{frame}\n\n'

  # function to add image
  def include_graphics(self,image,caption=''):
    self.text += '\\begin{figure}[h]\n'
    self.text += '\\includegraphics[width=.75\\textwidth,height=.75\\textheight]{'
    self.text += image + '}\n'
    self.text += '\\caption{'+caption+'}\n'
    self.text += '\\end{figure}\n'

  # function to end document and produce output
  def end(self):
    self.text += '\\end{document}'
    # create .tex file
    print(self.text,file=open(self.out_path+'.tex','w'))
    # compile
    os.system('pdflatex {}.tex -output-directory {}'.format(self.out_path, self.out_dir))
    # move auxilary files
    for ext in ['.aux','.nav','.pdf','.toc','.log','.out','.snm','.log']:
      if os.path.isfile('./'+self.out_name+ext):
        os.rename('./'+self.out_name+ext,self.out_path+ext)

class Directory(object):
  ddir = ""
  odir = ""
  def __init__(self):
    # TODO : put this information in a text or xml file for configuration
    # Sort out Directories
    brian_file = "C:/Users/Nexus/Desktop/covid/path_flag.txt"
    brian_laptop = "C:/Users/DuxLiteratum/Desktop/covid/path_flag.txt"
    brian_mbp = "/Users/brianbell/Box Sync/COVIDdata/path_flag.txt"
    # please add "path_flag.txt" to the directory where you keep the data
    toner_file = "/Users/briantoner/Documents/arizona/covid/flag.txt"
    sarah_file = "C:/Users/spwiz/Documents/GitHub/patient_trajectories/path_flag.txt"
    molly_file = "/Users/purpleacadia/Dropbox/BUMCT_Projects/COVID19-DataSci/Analysis_PtTrajectories/path_flag.txt"
    adrienne_laptop = "/Users/Adrienne/Desktop/Grad School/Projects/COVID/patient_trajectories/path_flag.txt"
    adrienne_file = "C:/Users/Adrienne/Documents/Projects/COVID/patient_trajectories/path_flag.txt"
    # also add your data path here for ddir (data sources) and odir (output location)
    if (os.path.isfile(brian_file)):
        self.ddir = "c:/Users/Nexus/Desktop/covid/box/Box Sync/COVIDdata/"
        self.odir = "C:/Users/Nexus/Desktop/covid/box/Box Sync/COVIDdata/odir/"
    elif (os.path.isfile(brian_laptop)):
        self.ddir = "C:/Users/DuxLiteratum/Desktop/covid/box/Box Sync/COVIDdata/"
        self.odir = "C:/Users/DuxLiteratum/Desktop/covid/box/Box Sync/COVIDdata/odir/"
    elif (os.path.isfile(brian_mbp)):
        self.ddir = "/Users/brianbell/Box Sync/COVIDdata/"
        self.odir = "/Users/brianbell/Box Sync/COVIDdata/odir/"
    elif (os.path.isfile(toner_file)):
        self.ddir = "/Users/briantoner/Box Sync/COVIDdata/"
        self.odir = "/Users/briantoner/Box Sync/COVIDdata/odir/"
        #self.odir = "/Users/briantoner/Documents/arizona/covid/data/"
    elif (os.path.isfile(molly_file)):
        self.ddir = "/Users/purpleacadia/Box/UABoxHealth/COVIDdata/odir/"
        self.odir = "/Users/purpleacadia/Box/UABoxHealth/COVIDdata/odir/"
    elif (os.path.isfile(adrienne_file)):
        self.ddir = "C:/Users/Adrienne/Box Sync/COVIDdata/"
        self.odir = "C:/Users/Adrienne/Documents/Projects/COVID/"
    elif (os.path.isfile(adrienne_laptop)):
        self.ddir = "/Users/Adrienne/Box Sync/COVIDdata/"
        self.odir = "/Users/Adrienne/Desktop/Grad School/Projects/COVID/"
    elif (os.path.isfile(sarah_file)):
        self.ddir = "C:/Users/spwiz/Box Sync/COVIDdata/"
        self.odir = "C:/Users/spwiz/Box Sync/COVIDdata/odir/"
    else:
        raise SystemExit('Error: Cannot find ddir.')

class ColumnInfo(object):
  fi = "ColumnInfo.csv"
  di = ""
  def __init__(self, fi):
    self.fi = fi
    if os.path.isfile(fi):
      self.di = pd.read_csv(fi)
    else:
      print("Warning : Missing ColumnInfo csv file!")

  # only do this once...
  def generate(self, df):
    dit = pd.DataFrame()
    dit["columns"] = df.columns
    dit["contains_string"] = 0
    dit["training_spoiler"] = 0
    for col in df.columns:
      test = df[col]
      testt = any(isinstance(val, str) for val in test)
      if (testt):
        dit["contains_string"][dit["columns"] == col] = 1
    if (self.di == ""):
      self.di = dit
    else:
      # this might be sketchy...
      self.di = pd.merge(di, dit, how="outer", on=['columns', 'contains_string', 'training_spoiler'])
    fo = fi
    di.to_csv(fo, mode="w", header=True, sep=",", index=False)

  def GetFrame(self):
    return self.di


irrelevantTests = ('nan',
                   'digoxin',
                   'carbamazepine',
                   'lithium',
                   'phenobarbital',
                   'valproic acid',
                   'phenytoin',
                   'glucagon',
                   'theophylline',
                   'Metanephrine, Random Urine',
                   'meperidine',
                   'Potassium, Feces',
                   'Brucella IgG',
                   'Brucella IgM',
                   'Metanephrines, Total, Random Urine',
                   'Normetanephrine, Random Urine',
                   'Creatinine, Random Urine',
                   'Neuron Specific Enolase',
                   'PSA, Free',
                   'PSA, Total',
                   'DHEA Level',
                   'Chloride, Feces',
                   'Creatinine, Timed Urine',
                   'Sodium, Feces'
                   'Norepinephrine Level',
                   'Dopamine Level',
                   'Epinephrine Level',
                   'Interleukin-2 (IL-2) (RL)',
                   'Interleukin-2 (IL-2)',
                   'IL-2',
                   'hepC_RNA',
                   'hepCRNA_log',
                   'Bilirubin, UR',
                   'biliUr',
                   'esotericTest',
                   'basophils_Fluid%',
                   'beta2Glycoprotein1_IgA',
                   'alkphos_bone',
                   'Norepinephrine Level',
                   'metanephrine',
                   'metanephrine_tot',
                   'normetanephrine',
                   'C. pneumoniae IgG',
                   'c_pnaIgG',
                   'specificGravity',
                   'aldolase',
                   'pathologist',
                   'timeFrozenResultCalled',
                   'resultsCalledTo',
                   'beta2Glycoprotein1_IgM',
                   'Sodium, Feces',
                   'Beta-2-Microglobulin',
                   'hepB_quantDNA'
                   )

def dropIrrelevantTests(df):
    df.drop(irrelevantTests, axis=1 ,inplace=True)
    return df


def relabelTests_ce(df):

    #convert weights in lbs to kg (will relabel all as "weight" further down)
    df.loc[df.TEST=='Weight (lb)',['RESULT_VAL']]=pd.to_numeric(df.RESULT_VAL[df.TEST=='Weight (lb)'], errors='coerce')
    df.loc[df.TEST=='Weight (lb)',['RESULT_VAL']]=df.RESULT_VAL[df.TEST=='Weight (lb)']*0.4536
    df.loc[df.TEST=='Weight (lb)',['UNITS']]='Kilogram'

    #convert heights in inches to cm (will relabel all as "height" further down)
    df.loc[df.TEST.isin(['Height Calculation','Height (in)']),['RESULT_VAL']]=pd.to_numeric(df.RESULT_VAL[df.TEST.isin(['Height Calculation','Height (in)'])], errors='coerce')
    df.loc[df.TEST.isin(['Height Calculation','Height (in)']),['RESULT_VAL']]=df.RESULT_VAL[df.TEST.isin(['Height Calculation','Height (in)'])]*2.54
    df.loc[df.TEST.isin(['Height Calculation','Height (in)']),['UNITS']]='Centimeter'

    labels = {
    'Chloride':'chloride',
    'Respiratory Rate': 'RR',
    'Coronavirus (COVID-19) SARS-CoV-2 RNA':'COVID_pcr',
    'Glucose Level': 'glucose',
    'Systolic Blood Pressure' : 'SBP',
    'Diastolic Blood Pressure' : 'DBP',
    'BP_DIA':'SBP',
    'BP_SYS':'DBP',
    'Heart Rate Monitored' : 'HEART_RT',
    'Height (in)':  'height',
    'Height' : 'height',
    'HEIGHT':'height',
    'Bilirubin, UR': 'biliUr',
    'BUN/Creat Ratio': 'bun/Cr',
    'Oxygen Therapy': 'O2device',
    'Temperature (F)': 'temp',
    'Weight':'weight',
    'Weight (lb)':'weight',
    'WEIGHT':'weight',
    'BMI (Pt Care)' : 'BMI',
    'Glasgow Coma Score': 'GCS',
    'Heart Rate EKG' : 'HR',
    'Lymphocytes %': 'lymph%',
    'Bilirubin Total' : 'biliT',
    'NT-proBNP' : 'BNP',
    'Lymphocytes #': 'lymph#',
    'D-Dimer, Quant': 'd-dimer',
    'ED Document Glasgow Coma Scale' : 'GCS',
    'Platelet': 'platelets',
    'C Reactive Protein' : 'CRP',
    'Ferritin Level': 'Ferritin',
    'eGFR (non-African Descent)': 'GFR',
    'O2 Sat, ABG POC' : 'SpO2',
    'D-Dimer Quantitative' : 'd-dimer',
    'Troponin-T, High Sensitivity': 'tropT_hs',
    'Troponin T, High Sensitivity': 'tropT_hs',
    'Cholesterol/HDL Ratio' : 'cholesterol/HDL',
    'Bilirubin  Direct' : 'biliD',
    'Height Calculation' : 'height',
    'HEIGHT':'height',
    'Non HDL Cholesterol': 'chol_NonHDL',
    'Inspiratory Time': 'vent_iTime',
    'Transcribed Height (cm)' : 'height',
    'CRP High Sens' : 'CRP_hs',
    'MSOFA Score' : 'mSOFA',
    'FIO2, Arterial POC':'FiO2',
    'FIO2':'FiO2',
    'HCO3(Bicarb), ABG POC': 'bicarb',
    'Peak Inspiratory Pressure': 'vent_PIP',
    'Coronavirus(COVID-19)SARS CoV2 TL Result' : 'COVID_tl',
    'Ventilator Mode': 'vent_mode',
    'Ventilator Frequency, Mandatory': 'vent_RRset',
    'Inspiratory to Expiratory Ratio': 'vent_IE',
    'Positive End Expiratory Pressure': 'vent_PEEP',
    'Auto-PEEP': 'vent_autoPEEP',
    'End Expiratory Pressure' : 'vent_PEEP',#need to reassess O2 device that goes with this one to be sure it is vent
    'PEEP.':'vent_PEEP',  #need to reassess O2 device that goes with this one to be sure it is vent
    'PCO2, ABG POC':'pCO2',
    'Inspiratory Flow Rate' : 'vent_iFlow',
    'Bilirubin Direct Serum' : 'biliD',
    'Inspiratory Pressure' : 'vent_inspP', #need to check this one goes with vent too
    'Inspiratory to Expiratory Ratio Measured' : 'vent_IE',
    'Interleukin-2 (IL-2)' : 'IL-2',
    'Interleukin-2 (IL-2) (RL)' : 'IL-2',
    'PO2, VBG POC':'PvO2',
#these below are from additional labs obtained in December
    'Potassium':'potassium',
    'Albumin':'albumin',
    'PO2, ABG POC': 'PaO2',
    'Fibrinogen Activity':'fibrinogen',
    'Sodium':'sodium',
    'INR':'INR',
    'pH, ABG POC':'pH',
    'pH, VBG POC':'pH',
    'Sodium, POC':'sodium',
    'pH, ABG':'pH',
    'Lactate, Venous':'lactate',
    'pH, VBG':'pH',
    'Potassium, POC':'potassium',
    'Lipase Level':'lipase',
    'PO2, ABG':'PaO2',
    'PO2, VBG':'PvO2',
    'Albumin, PES':'albumin',
    'Potassium, VBG':'potassium',
    'Potassium, ABG':'potassium',
    'Sodium, VBG':'sodium',
    'Sodium, ABG':'sodium',
    'INR MAR':'INR',  # unsure what MAR is but these look like typical INR values
    'Alkaline Phosphatase':'alk_phos',
    'Magnesium':'magnesium'
    }

    #replace labels
    df.replace(labels,inplace=True)

    return df

def relabelLabs_labs(df):
  #define shortened lab labels
  lablabels = {
    'Creatinine':'creatinine',
    'Monocytes %':'monocyte%',
    'Chloride':'chloride',
    'Monocytes #': 'monocyte#',
    'Anion Gap':'anionGap',
    'Basophils #':'basophils#',
    'Lymphocytes %':'lymph%',
    'Albumin':'albumin',
    'Lymphocytes #':'lymph#',
    'Metamyelocytes #': 'metamyelocytes#',
    'Myelocytes #': 'myelocytes#',
    'Basophils %':'basophils%',
    'Lipase Level':'lipase',
    'Hemoglobin A1c':'A1C',
    'Non HDL Cholesterol':'chol_NonHDL',
    'Beta-Hydroxybutyrate':'betaHydroxybutyrate',
    'Salicylate Level':'salicylateLevel',
    'LDL, Calculation':'LDL_calc',
    'Promyelocytes #': 'promyelocytes#',
    'Myelocytes %':'myelocytes%',
    'Retic #':'retic#',
    'Cholesterol/HDL Ratio': 'cholesterol/HDL',
    'Exp date':'expDate',
    'Ammonia':'ammonia',
    'Protein C Activity':'proteinC_activity',
    'Metamyelocytes %': 'metamyelocytes%',
    'Acetaminophen Level':'acetaminophen_level',
    'Cardiolipin IgA Antibody':'cardiolipin_IgA',
    'Prealbumin':'prealbumin',
    'Hep B Surface Ab Result':'hepBs_Ab',
    'Promyelocytes %': 'promyelocytes%',
    'Vitamin B12 Level':'vitB12',
    'C. pneumoniae IgA': 'c_pnaIgA',
    'Vitamin D, 1, 25 (OH) Total': '1,25-vitaminD',
    'Cardiolipin IgM Antibody':'cardiolipin_IgM',
    'Rheumatoid Factor':'rheumatoidFactor',
    'Activated Clotting Time POC': 'ACT',
    'Metanephrine, Free': 'metanephrine_free',
    'Plasma Hemoglobin': 'HGB',
    'Other Cells %':'otherCells%',
    'Basophils, Body Fluid %':'basophils_Fluid%',
    'Dev lot number': 'dev_Lot#',
    'Card lot number': 'card_Lot#',
    'C. pneumoniae IgG': 'c_pnaIgG',
    'Alpha-1-Antitrypsin': 'alpha1-antitrypsin',
    'Renin Activity, Plasma': 'renin-activity_plasma',
    'Specific Gravity, BF': 'specificGravity',
    'Complement, Total (CH50)': 'complementTot',
    'Cardiolipin IgG Antibody': 'cardiolipin_IgG',
    'Aldosterone': 'aldosterone',
    'HCV RNA, PCR, Quant (IU/mL)': 'hepC_RNA',
    'Other Cells #': 'otherCells#',
    'HCV RNA, PCR, Quant (LogIU/mL)':'hepCRNA_log',
    'Beta-2-Microglobulin':'Beta-2-Microglobulin',
    'Normetanephrine, Free':'normetanephrine_free',
    'PTH, Related Protein':'PTHrP',
    'Aldolase':'aldolase',
    'Results Reported To':'resultsCalledTo',
    'Time Frozen Result Called':'timeFrozenResultCalled',
    'Performing Pathologist':'pathologist',
    'Beta2- Glycoprotein 1 Ab IgA':'beta2Glycoprotein1_IgA',
    'Coxsackie A9 Ab':'coxsackieA9_Ab',
    'Esoteric Test Name':'esotericTest',
    'Prolactin':'prolactin',
    'Alkaline Phosphatase, Bone Specific':'alkphos_bone',
    'Beta2- Glycoprotein 1 Ab IgM': 'beta2Glycoprotein1_IgM',
    'Coxsackie A4 Ab': 'coxsackieA4_Ab',
    'Platelet Count, Citrated': 'platelets',
    'ACTH':'ACTH',
    'Normetanephrine':'normetanephrine',
    'Metanephrine':'metanephrine',
    'Vitamin B6 level':'vitaminB6',
    'Metanephrines, Total':'metanephrine_tot',
    #from labs sheet, not in clinical events sheet:
    'glucose':'glucose',
    'Vitamin D, 25-OH, Total':'25-vitaminD',
    'Vitamin D, 25-OH, D3':'25-vitaminD',
    'Hepatitis B DNA, Quant PCR (IU/mL)':'hepB_quantDNA',
    #these below are also in relabelTests_ce, duplicated here
    # so can run just this function on labs.csv and capture all labs
    'PO2, ABG':'PaO2',
    'PO2, VBG':'PvO2',
    'Albumin, PES':'albumin',
    'Potassium, VBG':'potassium',
    'Potassium, ABG':'potassium',
    'Sodium, VBG':'sodium',
    'Sodium, ABG':'sodium',
    'INR MAR':'INR',  # unsure what MAR is but these look like typical INR values
    'Alkaline Phosphatase':'alk_phos',
    'Magnesium':'magnesium',
    'INR':'INR',
    'pH, ABG POC':'pH',
    'pH, VBG POC':'pH',
    'PO2, VBG':'PvO2',
    'Sodium, POC':'sodium',
    'pH, ABG':'pH',
    'Lactate, Venous':'lactate',
    'pH, VBG':'pH',
    'PO2, ABG POC': 'PaO2',
    'Fibrinogen Activity':'fibrinogen',
    'Sodium':'sodium',
    'Potassium':'potassium',
    'Potassium, POC':'potassium'
    }
  df.replace(lablabels, inplace=True)

  return df

def relabelO2(df, sw):
  #define non-redundant O2 delivery device types
  #we will use types roomAir, NC (nasal cannula), hiFlowNC (highFlowNC flow nasal cannula),
  #  openMask (any venti mask, face tent, simple mask, etc), nonRebreather, NIPPV (cpap/bipap),
  #  BVM (bag valve mask), vent (ventilator), trach mask, and t-piece
  #When two devices ar listed, we will take the one with greater O2 delivery or greater invasiveness
    O2devices = {
    'Room air':'roomAir',

    'Nasal cannula':'NC',
    'Room air, Nasal cannula':'NC',
    'Humidification, Nasal cannula':'NC',

    'High-Flow nasal cannula':'hiFlowNC',
    'High-Flow nasal cannula, Humidification':'hiFlowNC',
    'High-Flow nasal cannula, Nasal cannula':'hiFlowNC',
    'High-Flow nasal cannula, Humidification, Nasal cannula':'hiFlowNC',
    'High-Flow nasal cannula, Venti-mask':'hiFlowNC',
    'High-Flow nasal cannula, Oxymask':'hiFlowNC',
    'High-Flow nasal cannula, Humidification, Venti-mask':'hiFlowNC',

    'Aerosol mask':'openMask',
    'Simple mask':'openMask',
    'Oxymask':'openMask',
    'Room air, Venti-mask':'openMask',
    'Venti-mask':'openMask',
    'Humidification':'openMask',
    'Room air, Simple mask':'openMask',
    'Nasal cannula, Venti-mask':'openMask',
    'Blow-By':'openMask',
    'Mist tent':'openMask',
    'Nasal cannula, Simple mask':'openMask',
    'Aerosol mask, Humidification':'openMask',
    'Face shield':'openMask',
    'Simple mask, Venti-mask':'openMask',
    'Face shield, Nasal cannula':'openMask',
    'Humidification, Simple mask':'openMask',
    'Nasal cannula, Oxymask':'openMask',

    'Nonrebreather mask':'nonRebreather',
    'High-Flow nasal cannula, Nonrebreather mask':'nonRebreather',
    'High-Flow nasal cannula, Nonrebreather mask, Venti-mask':'nonRebreather',
    'High-Flow nasal cannula, Humidification, Nonrebreather mask':'nonRebreather',
    'Partial rebreather mask':'nonRebreather',
    'Humidification, Nasal cannula, Nonrebreather mask':'nonRebreather',
    'Nasal cannula, Nonrebreather mask':'nonRebreather',
    'Humidification, Nasal cannula, Simple mask':'nonRebreather',
    'Room air, Nonrebreather mask':'nonRebreather',
    'Nonrebreather mask, Partial rebreather mask':'nonRebreather',
    'Nasal cannula, Nonrebreather mask, Venti-mask':'nonRebreather',
    'Nonrebreather mask, Venti-mask':'nonRebreather',

    'CPAP':'NIPPV',
    'BiPAP':'NIPPV',
    'BiPAP, Venti-mask':'NIPPV',
    'CPAP, Venti-mask':'NIPPV',
    'Room air, BiPAP':'NIPPV',

    'Bag valve mask':'BVM',

    'Ventilator':'vent',
    'Humidification, Ventilator':'vent',
    'CPAP, Ventilator':'vent',
    'Trach shield, Ventilator':'vent',

    'Trach shield':'trachMask',
    'Transtracheal (TTO)':'trachMask',
    'Trach shield, Transtracheal (TTO)': 'trachMask',
    'Aerosol mask, Blow-By, Simple mask, Transtracheal (TTO)':'trachMask',

    'Room air, T-piece':'t-piece',
    'T-piece':'t-piece',

    #for a few of these where the 2 listed devices are very different (vent vs not, trach vs not)
    #  we will preserve the ambiguity for now
    'High-Flow nasal cannula, Transtracheal (TTO)':'trachMask vs hiFlowNC',
    'Nasal cannula, Transtracheal (TTO)':'trachMask vs NC',
    'Nasal cannula, Ventilator':'vent vs NC',
    'Ventilator, Venti-mask':'vent vs openMask',
    'Simple mask, Ventilator':'vent vs openMask',
    'Room air, Ventilator':'vent vs roomAir',
    'High-Flow nasal cannula, Ventilator':'vent vs hiFlowNC',
    'Nonrebreather mask, Ventilator':'vent vs nonRebreather',
    'High-Flow nasal cannula, Ventilator, Venti-mask':'vent vs hiFlowNC'}
    #df.replace(O2devices, inplace=True)
    test = df.replace(O2devices, inplace=False)
    # note that if you feed in the whole data frame, this may do silly
    #      things
    sw.wd("FIO2 : Replaced {} redundant values".format(sum(test != df)))
    return df

# function to obtain dictionaries for numaric and nonnumeric values for labels
##Input dataframe, col1 is the name of the column that gives the test names, col2 is the name of the column with the values
def nonnumeric(dd, col1, col2):
    unique_tests = pd.unique(dd[col1])

    numvals = dict()
    nonnumvals = dict()
    for test in unique_tests:
        sid = dd[col1] == test
        dis = dd[sid]

        unique_vals = pd.unique(dis[col2])

        digitvals = []
        nondigitvals = []
        for v in unique_vals:
            try:
                float(v)
                digitvals.append(v)

            except ValueError:
                nondigitvals.append(v)

        numvals[test] = digitvals
        nonnumvals[test] = nondigitvals

    return numvals, nonnumvals

# function clean fio2 vals
def clean_fio2_val(text):
  # if str, look for numeric string
  if type(text) is str:
    # if no digits, return nan
    exp = re.compile('\d')
    match = re.findall(exp,text)
    if len(match) == 0:
      return np.nan
    # if there are digits, convert to float
    # multiply by 0.01 to convert from pct if applicable
    if '%' in text:
      pct_fact = 0.01
    else:
      pct_fact = 1
    # convert from lpm if applicable
    if 'lpm' in text:
      lpm_flag=True
    else:
      lpm_flag=False
    exp = re.compile('[^0-9\.]')
    new = float(re.sub(exp,'',text))
    if lpm_flag:
      new = 0.2+0.04*new
    return new * pct_fact
  # if float, do nothing
  elif type(text) is float:
    return text
  # if int, make float
  elif type(text) is int:
    return float(text)
  # if type not found, return warning and nan
  else:
    print('Warning: {} type {} not supported. Returning nan'.format(text,type(text)))
    return np.nan

# function to clean fio2 column
def clean_fio2_col(column, sw):
  # if series, convert to list
  if type(column) is pd.core.series.Series:
    column = column.values
  # initialize array of indices to drop
  replace = np.zeros(len(column))
  # loop
  for idx, val in enumerate(column):
    # clean val, make replace array if nan
    new = clean_fio2_val(val)
    column[idx] = new
    if np.isnan(new):
      replace[idx] = 1
  sw.wd("fio2_col: replaced {} values".format(replace.sum()))
  return column, replace


# function to clean column of miscellaneous string values
def clean_col(column, sw):
  # if series, convert to list
  if type(column) is pd.core.series.Series:
    column = column.values
  # initialize array of indices to drop
  replace = np.zeros(len(column))
  # loop
  for idx, val in enumerate(column):
    # clean val, make replace array if nan
    new = clean_string(val)
    column[idx] = new
    if np.isnan(new):
      replace[idx] = 1
  sw.wd("Replaced {} suspect values".format(replace.sum()))
  return np.array(column, dtype=float), replace

# function to remove inequality
def clean_string(val):
  # if str, clean
  if type(val) is str:
    # purely numeric, return as float
    exp = re.compile('[^0-9\.]')
    match = re.findall(exp,val)
    if len(match) == 0:
      return float(val)
    # if no ineq, return orig, otherwise remove and convert to float
    exp = re.compile('[\<\>]')
    match = re.findall(exp,val)
    if len(match) > 0:
      new = float(re.sub(exp,'',val))
      return new

    # if neither apply, then replace with nan
    return np.nan
  # don't change if it's not a string
  else:
    return val

# function to clean column of ratios
def clean_ratio_col(column, sw):
  # if series, convert to list
  if type(column) is pd.core.series.Series:
    column = column.values
  # initialize array of indices to drop
  replace = np.zeros(len(column))
  # loop
  for idx, val in enumerate(column):
    # clean val, make replace array if nan
    new = clean_ratio(val)
    column[idx] = new
    if np.isnan(new):
      replace[idx] = 1
  sw.wd("clean_ratio_col : replaced {} ratio columns ".format(replace.sum()))
  return column, replace

# function to fix ratios
def clean_ratio(val):
  # if str, clean
  if type(val) is str:
    # purely numeric, return as float
    exp = re.compile('[^0-9\.]')
    match = re.findall(exp,val)
    if len(match) == 0:
      try:
        return float(val)
      except:
        return np.nan
    # if : is there, compute decimal
    exp = re.compile('([0-9\.]*)\:([0-9\.]*)')
    match = re.search(exp,val)
    if match:
      # try to return as decimal, if doesn't work, return nan
      try:
        return float(match[1]) / float(match[2])
      except:
        return np.nan


    # if neither apply, then replace with nan
    return np.nan
  # don't change if it's not a string
  else:
    return val

# function to clean column of positive/negatives
def clean_posneg_col(column, sw):
  # if series, convert to list
  if type(column) is pd.core.series.Series:
    column = column.values
  # initialize array of indices to drop
  replace = np.zeros(len(column))
  # loop
  for idx, val in enumerate(column):
    # clean val, make replace array if nan
    new = clean_posneg(val)
    column[idx] = new
    if np.isnan(new):
      replace[idx] = 1
  sw.wd("clean_posneg_col : Replaced {} values".format(replace.sum()))
  return column, replace

# function to fix positive/negative
def clean_posneg(val):
  # if str, clean
  if type(val) is str:
    # purely numeric, return as float
    exp = re.compile('[^0-9\.]')
    match = re.findall(exp,val)
    if len(match) == 0:
      try:
        return float(val)
      except:
        return np.nan
    # Possible strings for 1
    pos_strings = ['Detected','DETECTED','Positive']
    neg_strings = ['Not Detected','Not detected','NOT DETECTED','Negative']

    if val in pos_strings:
      return 1.0

    elif val in neg_strings:
      return 0.0

    else:
      return np.nan

  else:
    return val

  # function to clean column of positive/negatives
def clean_gcs_col(column, sw):
  # if series, convert to list
  if type(column) is pd.core.series.Series:
    column = column.values
  # initialize array of indices to drop
  replace = np.zeros(len(column))
  # loop
  for idx, val in enumerate(column):
    # clean val, make replace array if nan
    new = clean_gcs(val)
    column[idx] = new
    if np.isnan(new):
      replace[idx] = 1
  sw.wd("clean_gcs_col : Replaced {} values".format(replace.sum()))
  return column, replace

# function to fix positive/negative
def clean_gcs(val):
  # if str, clean
  if type(val) is str:
    # purely numeric, return as float if between 3 and 15
    exp = re.compile('[^0-9\.]')
    match = re.findall(exp,val)
    if len(match) == 0:
      if float(val) >=3 and float(val) <=15:
        return float(val)
      else:
        return np.nan

    else:
      return np.nan

  else:
    return val

# Function to identify individual encounters
def identify_encntrs(di, sw):
  di['ENCNTR']=np.ones(len(di))
  di.loc[(di.HOSPITAL_DAY<0), 'ENCNTR']=0
  grouped=di.groupby(["RECORD_ID"])
  count = 0
  count_t = 0
  for group in grouped:
    if len(group[1][group[1]['ENCOUNTER_DAY']>0])>0:
      encntrs=pd.to_datetime(np.unique(group[1][group[1]['ENCOUNTER_DAY']==0]['VERIFIED_DT']))
      encntr_num=1
      for i in range(1,len(encntrs)):
          # TODO : count how many encounters per RECORD_ID
          # TODO : Check if patient goes more than 1 day without an
          #        observation
          count_t+=1
          if (encntrs[i]-timedelta(days=1))!=encntrs[i-1]:
            encntr_num+=1
            count+=1
          di.loc[((di.RECORD_ID==group[0]) & (encntrs[i]<=pd.to_datetime(di.VERIFIED_DT))), 'ENCNTR']=encntr_num
    else:
      count_t+=1
    # Measurements between encounters, or after last discharge date should be 1000
    #di.loc[((di.RECORD_ID==group[0]) & (di.HOSPITAL_DAY==1000)), 'ENCNTR']=1000
  sw.wd("Found {} total encounters among {} RECORD_IDs".format(count_t, len(grouped)))
  sw.wd("Found {} extra encounters among {} RECORD_IDs".format(count, len(grouped)))
  return di

def identify_vent(di, sw):
    di['VENT_FLAG']=np.zeros(len(di))
    di['VENT_DAY']=(-1)*np.ones(len(di))
    di['VENT_HOUR']=(-24)*np.ones(len(di))
    grouped = di.groupby(["RECORD_ID"])
    count = 0
    for group in grouped:
        vents=group[1][group[1]['TEST'].astype(str).str.contains("vent", case=False) |
                 group[1]['RESULT_VAL'].astype(str).str.contains('vent', case=False)]
        if vents.shape[0]>0:
          di.loc[(di.RECORD_ID==group[0]), 'VENT_FLAG']=1
          di.loc[(di.RECORD_ID==group[0]), 'VENT_DAY']=min(vents['VERIFIED_DT'])
          di.loc[(di.RECORD_ID==group[0]), 'VENT_HOUR']=min(vents[vents.VERIFIED_DT==min(vents["VERIFIED_DT"])]['VERIFIED_TM'])
          count+=1
    sw.wd("Found and marked {}/{} patients were ventilated".format(count, len(grouped)))
    return di

# TODO : Add code which analyzes text fields and replaces them with
#        numeric values (should have a dictionary of terms and
#        replacements.
#       -should probably read all of the input files, fix them, and
#        output "cleaned" input files so that we don't need to do that
#        every time.

def generate_dict(column, fo):
  dictionary = {}
  # get unique string values
  # for each unique string value
  # col_dict[string] = {}
  # col_dict[string]["original"] = string
  # col_dict[string]["suggested"] = clean_val(string)
  # col_dict[string]["replacement"] = ""
  # json.dump(col_dict, open(fo, 'w'))

class Cleaner(object):
  label_dict = {}
  value_dict = {}
  def __init__(self, ddir):
    label_file = ddir+"label_dict.txt"
    value_file = ddir+"value_dict.txt"
    self.label_dict = json.load(open(label_file))
    self.value_dict = json.load(open(value_file))

# rename colnames on our new data to match our old
def renamecols(df):
    colnamedict = {'TEST_RESULT':'RESULT_VAL','PERSON_ID':'RECORD_ID','LAB':'TEST','RESULTVAL':'RESULT_VAL',
                   'RESULT_UNITS':'UNITS','TEST_DT':'VERIFIED_DT','TEST_TM':'VERIFIED_TM','VITAL':'TEST','RESULT':'RESULT_VAL',
                  'DT':'VERIFIED_DT','TM':'VERIFIED_TM'}

    newcolnames = dict()
    for col in df.columns:
        if col in colnamedict.keys():
            newcolnames[col] = colnamedict.get(col)
        else:
            newcolnames[col] = col

    df = df.rename(columns = newcolnames)

    return df

#Removing rows based on the number of values in the row
##Inputs: df = dataframe, threshold = min number of values in each row, summary(T/F) = whether you
##want a summary printout
def removerows(df, threshold, summary):
    #Add values that represent missing values to this list
    di = df.replace([111.0,'-111.0',111,'111',-111.],np.nan)

    rowcount = di.count(axis = 'columns')

    #Summary generates barplot of values and a printout of number of rows above given value
    if summary == True:
        frequency = rowcount.value_counts()
        frequency = frequency.sort_index(ascending=False)
        frequency = frequency.cumsum()

        plt.bar(frequency.index, frequency.values)

        plt.xlabel('Number of Row Elements')
        plt.ylabel('Number of Rows')

        plt.grid(b=True, which='major', color='#666666', linestyle='-', alpha = 0.6)
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        plt.show()

        for index, value in frequency.items():
            print('Number of rows <=', index, 'elements: ', value, '(', round(value/len(di.index) * 100,3),'%)')

    newidx = rowcount[rowcount >= threshold]

    di = di.iloc[list(newidx.index)]
    di = di.set_index(pd.RangeIndex(start = 0, stop = len(di.index), step = 1))

    di = di.fillna(-111.0)

    return di


# function to find sensitivity and specificity to evaluate methods
def sens_spec(y, yhat):
    true_pos = sum(np.logical_and(y.values==1, yhat==1))
    sens = true_pos / sum(y)
    true_neg = sum(np.logical_and(y.values==0, yhat==0))
    spec = true_neg / (len(y) - sum(y))

    return sens, spec


#----- function to generate FPR, TPR with given thresholds
def roc_curve_thresholds(labl_list, prob_list, thresholds):

    positives= np.sum(labl_list)
    negatives= len(labl_list)-positives

    tpr= np.zeros(len(thresholds))
    fpr= np.zeros(len(thresholds))

    for idx,thresh in enumerate(thresholds):

        tpr[idx]= np.sum(((prob_list > thresh).astype(int)+labl_list)== 2)/positives
        fpr[idx]= 1-np.sum(((prob_list > thresh).astype(int)+labl_list)== 0)/negatives

    return fpr, tpr

#----- return Kolmogorov-Smirnov critical value for given n_trials and alpha
def ks_critical_value(n_trials, alpha):
    return ksone.ppf(1-alpha/2, n_trials)


# dataset generator
class data_gen(object):
  def __init__(self, data_file, pos_thresh=48, train_frac=0.8, seed=2020):
    self.data_file = data_file
    self.train_frac = train_frac
    self.pos_thresh = pos_thresh
    self.seed = seed

    # read in data
    full_data = pd.read_csv(data_file)
    full_data = full_data.loc[full_data['time_until_vent'] > 0]

    # identify predictors
    pred_idx = [('hour' not in col) & ('vent' not in col) & ('duration' not in col) for col in full_data.columns]
    predictors = full_data.columns[pred_idx][2:]

    # mark positive/negative based on pos_thresh
    full_data['vent'] = (full_data['time_until_vent'] <= pos_thresh).apply(int)

    # shuffle and split into train/test
    full_data = full_data.sample(frac=1,random_state=seed)
    ntrain = int(full_data.shape[0]*train_frac)
    train = full_data.iloc[:ntrain,]
    test = full_data.iloc[ntrain:,]

    # split into x and y, save data in variety of formats
    self.full_data = full_data
    self.train = train
    self.test = test
    
    self.xtrain = train[predictors]
    self.ytrain = train['vent']

    self.xtest = test[predictors]
    self.ytest = test['vent']
