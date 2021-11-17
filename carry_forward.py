import pandas as pd
import os
import numpy as np
from utils.utils import *

# set up markdown summary generator
directory = Directory()
ddir = directory.odir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

#if not os.path.isdir(odir+'cleaned/withTimestamp/'):
 # os.makedirs(odir+'cleaned/withTimestamp/')

#define time blocks used in this training set, in hours (goal 4 hr)
t_interval=4

#load data frame
fname=ddir+"covid_gen_all-{}".format(t_interval)
df=pd.read_csv(fname+".csv",low_memory=False)
   #low_memory=False prevents pandas refusing to guess column datatpyes

#define what value is used for "missing" values; will be converted to np.nan
missing=-111
missingStr='-111.0'

# make sure df is sorted by record_id, encounter, hour so value carry forward appropriately
df.sort_values(by=['RECORD_ID', 'ENCNTR','hour'],inplace=True)
df[df==missing]=np.nan  #set missing values to nan
df[df==missingStr]=np.nan

#limit is number of rows.

#define how long each class of values can be carrid forward
#  to denote how many rows to fill forward
limit_long=int(72.0/t_interval) #3 days for long interval
limit_short=int(12.0/t_interval)  #using 12 for now, goal only 8 hrs though

#long carry columns -- most labs
long_carry_cols=['HGB',
                    'HGB-hour',
                    'HGB_initial',
                    'HGB-hour_initial',
                    'WBC',
                    'WBC-hour',
                    'WBC_initial',
                    'WBC-hour_initial',
                    'RDW-CV',
                    'RDW-CV-hour',
                    'RDW-CV_initial',
                    'RDW-CV-hour_initial',
                    'MCH',
                    'MCH-hour',
                    'MCH_initial',
                    'MCH-hour_initial',
                    'RBC',
                    'RBC-hour',
                    'RBC_initial',
                    'RBC-hour_initial',
                    'BUN',
                    'BUN-hour',
                    'BUN_initial',
                    'BUN-hour_initial',
                    'glucose',
                    'glucose-hour',
                    'glucose_initial',
                    'glucose-hour_initial',
                    'chloride',
                    'chloride-hour',
                    'chloride_initial',
                    'chloride-hour_initial',
                    'platelets',
                    'platelets-hour',
                    'platelets-hour_initial',
                    'platelets_initial',
                    'MPV',
                    'MPV-hour',
                    'MPV_initial',
                    'MPV-hour_initial',
                    'lymph#',
                    'lymph#-hour',
                    'lymph#_initial',
                    'lymph#-hour_initial',
                    'MCV',
                    'MCV-hour',
                    'MCV_initial',
                    'MCV-hour_initial',
                    'Calcium',
                    'Calcium-hour',
                    'Calcium_initial',
                    'Calcium-hour_initial',
                    'GCS',
                    'GCS-hour',
                    'GCS_initial',
                    'GCS-hour_initial',
                    'd-dimer',
                    'd-dimer-hour',
                    'd-dimer_initial',
                    'd-dimer-hour_initial',
                    'MCHC',
                    'MCHC-hour',
                    'MCHC_initial',
                    'MCHC-hour_initial',
                    'CRP',
                    'CRP-hs',
                    'CRP-hour',
                    'CRP_initial',
                    'CRP-hour_initial',
                    'CRP_hs',
                    'CRP_hs-hour',
                    'CRP_hs_initial',
                    'CRP_hs-hour_initial',
                    'bun/Cr',
                    'bun/Cr-hour',
                    'bun/Cr_initial',
                    'bun/Cr-hour_initial',
                    'biliT',
                    'biliT-hour',
                    'biliT_initial',
                    'biliT-hour_initial',
                    'biliD',
                    'biliD-hour',
                    'biliD_initial',
                    'biliD-hour_initial',
                    'IL-2',
                    'IL-2-hour',
                    'IL-2_initial',
                    'IL-2-hour_initial',
                    'HCT',
                    'HCT-hour',
                    'HCT_initial',
                    'HCT-hour_initial',
                    'lymph%',
                    'lymph%-hour',
                    'lymph%_initial',
                    'lymph%-hour_initial',
                    'RDW-SD',
                    'RDW-SD-hour',
                    'RDW-SD_initial',
                    'RDW-SD-hour_initial',
                    'chol_NonHDL',
                    'chol_NonHDL-hour',
                    'chol_NonHDL_initial',
                    'chol_NonHDL-hour_initial',
                    'creatinine',
                    'creatinine-hour',
                    'creatinine_initial',
                    'creatinine-hour_initial',
                    'GFR',
                    'GFR-hour',
                    'GFR_initial',
                    'GFR-hour_initial',
                    'vent_inspP',
                    'vent_inspP-hour',
                    'vent_inspP_initial',
                    'vent_inspP-hour_initial',
                    'mSOFA',
                    'mSOFA-hour',
                    'mSOFA_initial',
                    'mSOFA-hour_initial',
                    'biliUr',
                    'biliUr-hour',
                    'biliUr_initial',
                    'biliUr-hour_initial',
                    'bicarb',
                    'bicarb-hour',
                    'bicarb_initial',
                    'bicarb-hour_initial',
                    'pCO2',
                    'pCO2_initial',
                    'pCO2-hour',
                    'pCO2-hour_initial',
                    'tropT_hs',
                    'tropT_hs-hour',
                    'tropT_hs_initial',
                    'tropT_hs-hour_initial',
                    'Cholesterol',
                    'Cholesterol-hour',
                    'Cholesterol_initial',
                    'Cholesterol-hour_initial',
                    'cholesterol/HDL',
                    'cholesterol/HDL-hour',
                    'cholesterol/HDL_initial',
                    'cholesterol/HDL-hour_initial',
                    'Ferritin',
                    'Ferritin-hour',
                    'Ferritin_initial',
                    'Ferritin-hour_initial',
                    'BNP',
                    'BNP-hour',
                    'BNP_initial',
                    'BNP-hour_initial',
                    'vent_mode',
                    'vent_mode-hour',
                    'vent_mode_initial',
                    'vent_mode-hour_initial',
                    'vent_RRset',
                    'vent_RRset-hour',
                    'vent_RRset_initial',
                    'vent_RRset-hour_initial',
                    'vent_PIP',
                    'vent_PIP-hour',
                    'vent_PIP_initial',
                    'vent_PIP-hour_initial',
                    'vent_IE',
                    'vent_IE-hour',
                    'vent_IE_initial',
                    'vent_IE-hour_initial',
                    'vent_PEEP',
                    'vent_PEEP-hour',
                    'vent_PEEP_initial',
                    'vent_PEEP-hour_initial',
                    'vent_autoPEEP',
                    'vent_autoPEEP-hour',
                    'vent_autoPEEP_initial',
                    'vent_autoPEEP-hour_initial',
                    'vent_iTime',
                    'vent_iTime-hour',
                    'vent_iTime_initial',
                    'vent_iTime-hour_initial',
                    'PEEP.',
                    'PEEP.-hour',
                    'PEEP._initial',
                    'PEEP.-hour_initial',
                    'vent_iFlow',
                    'vent_iFlow-hour',
                    'vent_iFlow_initial',
                    'vent_iFlow-hour_initial',

                    #other new
                    'monocyte%',
                    'monocyte%-hour',
                    'monocyte%_initial',
                    'monocyte%-hour_initial',
                    'monocyte#',
                    'monocyte#-hour',
                    'monocyte#_initial',
                    'monocyte#-hour_initial',
                    'anionGap',
                    'anionGap-hour',
                    'anionGap_initial',
                    'anionGap-hour_initial',
                    'basophils#',
                    'basophils#-hour',
                    'basophils#_initial',
                    'basophils#-hour_initial',
                    'lactate',
                    'lactate-hour',
                    'lactate_initial',
                    'lactate-hour_initial',
                    'lymph#',
                    'lymph#-hour',
                    'lymph#_initial',
                    'lymph#-hour_initial',
                    'metamyelocytes#',
                    'metamyelocytes#-hour',
                    'metamyelocytes#_initial',
                    'metamyelocytes#-hour_initial',

                    'myelocytes#',
                    'myelocytes#-hour',
                    'myelocytes#_initial',
                    'myelocytes#-hour_initial',
                    'basophils%',
                    'basophils%-hour',
                    'basophils%_initial',
                    'basophils%-hour_initial',
                    'A1C',
                    'A1C-hour',
                    'A1C_initial',
                    'A1C-hour_initial',
                    'betaHydroxybutyrate',
                    'betaHydroxybutyrate-hour',
                    'betaHydroxybutyrate_initial',
                    'betaHydroxybutyrate-hour_initial',
                    'salicylateLevel',
                    'salicylateLevel-hour',
                    'salicylateLevel_initial',
                    'salicylateLevel-hour_initial',
                    'LDL_calc',
                    'LDL_calc-hour',
                    'LDL_calc_initial',
                    'LDL_calc-hour_initial',
                    'promyelocytes%',
                    'promyelocytes%-hour',
                    'promyelocytes%_initial',
                    'promyelocytes%-hour_initial',
                    'myelocytes%',
                    'myelocytes%-hour',
                    'myelocytes%_initial',
                    'myelocytes%-hour_initial',
                    'retic#',
                    'retic#-hour',
                    'retic#_initial',
                    'retic#-hour_initial',
                    'ammonia',
                    'ammonia-hour',
                    'ammonia_initial',
                    'ammonia-hour_initial',
                    'amonia', #misspelling
                    'amonia-hour',
                    'amonia_initial',
                    'amonia-hour_initial',
                    'proteinC_activity',
                    'proteinC_activity-hour',
                    'proteinC_activity_initial',
                    'proteinC_activity-hour_initial',
                    'metamyelocytes%',
                    'metamyelocytes%-hour',
                    'metamyelocytes%_initial',
                    'metamyelocytes%-hour_initial',
                    'metameylocytes%_initial',
                    'acetaminophen_level',
                    'acetaminophen_level-hour',
                    'acetaminophen_level_initial',
                    'acetaminophen_level-hour_initial',
                    'cardiolipin_IgA',
                    'cardiolipin_IgA-hour',
                    'cardiolipin_IgA_initial',
                    'cardiolipin_IgA-hour_initial',
                    'prealbumin',
                    'prealbumin-hour',
                    'prealbumin_initial',
                    'prealbumin-hour_initial',
                    'hepBs_Ab',
                    'hepBs_Ab-hour',
                    'hepBs_Ab_initial',
                    'hepBs_Ab-hour_initial',
                    'promyelocytes%',
                    'promyelocytes%-hour',
                    'promyelocytes_initial',
                    'promyelocytes%-hour_initial',
                    'promyelocytes#',
                    'promyelocytes#-hour',
                    'promyelocytes#_initial',
                    'promyelocytes#-hour_initial',
                    'vitB12',
                    'vitB12-hour',
                    'vitB12_initial',
                    'vitB12-hour_initial',

                    'c_pnaIgG',
                    'c_pnaIgG-hour',
                    'c_pnaIgA_initial',
                    'c_pnaIgA-hour_initial',
                    'c_pnaIgG',
                    'c_pnaIgG-hour',
                    'c_pnaIgG_initial',
                    'c_pnaIgG-hour_initial',
                    '1,25-vitaminD',
                    '1,25-vitaminD-hour',
                    '1,25-vitaminD-hour_initial',
                    '1,25-vitaminD_initial',
                    'cardiolipin_IgM',
                    'cardiolipin_IgM-hour',
                    'cardiolipin_IgM_initial',
                    'cardiolipin_IgM-hour_initial',
                    'rheumatoidFactor',
                    'rheumatoidFactor-hour',
                    'rheumatoidFactor_initial',
                    'rheumatoidFactor-hour_initial',
                    'ACT',
                    'ACT-hour',
                    'ACT_initial',
                    'ACT-hour_initial',
                    'metanephrine_free',
                    'metanephrine_free-hour',
                    'metanephrine_free_initial',
                    'metanephrine_free-hour_initial',
                    'otherCells%',
                    'otherCells%-hour',
                    'otherCells%_initial',
                    'otherCells%-hour_initial',
                    'basophils_Fluid%',
                    'basophils_Fluid%-hour',
                    'basophils_Fluid%_initial',
                    'basophils_Fluid%-hour_initial',
                    'c_pnaIgG',
                    'c_pnaIgA-hour',
                    'c_pnaIgA_initial',
                    'alpha1-antitrypsin',
                    'alpha1-antitrypsin-hour',
                    'alpha1-antitrypsin_initial',
                    'alpha1-antitrypsin-hour_initial',
                    'renin-activity_plasma',
                    'renin-activity_plasma_initial',
                    'renin-activity_plasma-hour',
                    'renin-activity_plasma-hour_initial',
                    'PTHrP',
                    'PTHrP-hour',
                    'PTHrP_initial',
                    'aldolase',
                    'aldolase-hour',
                    'aldolase_initial',
                    'aldolase-hour_initial',
                    'beta2Glycoprotein1_IgA',
                    'beta2Glycoprotein1_IgA-hour',
                    'beta2Glycoprotein1_IgA_initial',
                    'beta2Glycoprotein1_IgA-hour_initial',
                    'coxsackieA9_Ab',
                    'coxsackieA9_Ab-hour',
                    'coxsackieA9_Ab_initial',
                    'esotericTest',
                    'esotericTest-hour',
                    'esotericTest_initial',
                    'esotericTest-hour_initial',
                    'prolactin',
                    'prolactin-hour',
                    'prolactin_initial',
                    'prolactin-hour_initial',
                    'alkphos_bone',
                    'alkphos_bone-hour',
                    'alkphos_bone_initial',
                    'alkphos_bone-hour_initial',
                    'beta2Glycoprotein1_IgM',
                    'beta2Glycoprotein1_IgM-hour',
                    'beta2Glycoprotein1_IgM_initial',
                    'beta2Glycoprotein1_IgM-hour_initial',
                    'coxsackieA4_Ab',
                    'coxsackieA4_Ab-hour'
                    'coxsackieA4_Ab_initial',
                    'coxsackieA4_Ab-hour_initial',
                    'ACTH',
                    'ACTH-hour',
                    'ACTH_initial',
                    'ACTH-hour_initial',
                    'normetanephrine',
                    'normetanephrine-hour',
                    'normetanephrine_initial',
                    'normetanephrine-hour_initial',
                    'metanephrine',
                    'metanephrine-hour',
                    'metanephrine_initial',
                    'metanephrine-hour_initial',
                    'vitaminB6'
                    'vitaminB6-hour',
                    'vitaminB6_initial',
                    'vitaminB6-hour_initial',
                    'metanephrine_tot',
                    'metanephrine_tot-hour',
                    'metanephrine_tot_initial',
                    'metanephrine_tot-hour_initial',
                    '25-vitaminD',
                    '25-vitaminD-hour',
                    '25-vitaminD_initial',
                    '25-vitaminD-hour_initial',
                    'hepB_quantDNA',
                    'hepB_quantDNA-hour',
                    'hepB_quantDNA_initial',
                    'hepB_quantDNA-hour_initial',
                    'expDate',
                    'expDate-hour',
                    'expDate_initial',
                    'expDate-hour_initial',
                    'fibrinogen',
                    'fibrinogen-hour',
                    'fibrinogen_initial',
                    'fibrinogen-hour_initial',
                    'aldosterone',
                    'aldosterone-hour',
                    'aldosterone_initial',
                    'aldosterone-hour_initial',
                    'nan',
                    'nan-hour',
                    'nan_initial',
                    'nan-hour_initial',
                    'otherCells#',
                    'otherCells#-hour',
                    'otherCells#_initial',
                    'otherCells#-hour_initial',
                    'dev_Lot#',
                    'dev_Lot#-hour',
                    'dev_Lot#_initial',
                    'dev_Lot#-hour_initial',
                    'card_Lot#',
                    'card_Lot#-hour',
                    'card_Lot#_initial',
                    'card_Lot#-hour_initial',
                    'cardiolipin_IgG',
                    'cardiolipin_IgG-hour',
                    'cardiolipin_IgG_initial',
                    'cardiolipin_IgG-hour_initial',
                    'complementTot',
                    'complementTot-hour',
                    'complementTot_initial',
                    'complementTot-hour_initial',
                    'normetanephrine_free',
                    'normetanephrine_free-hour',
                    'normetanephrine_free_initial',
                    'normetanephrine_free-hour_initial',
                    'vitaminB6',
                    'vitaminB6-hour',
                    'vitaminB6_initial',
                    'Norepinephrine Level',
                    'Norepinephrine Level-hour',
                    'Norepinephrine Level_initial',
                    'Norepinephrine Level-hour_initial',
                    'metanephrine',
                    'metanephrine-hour',
                    'metanephrine_initial',
                    'metanephrine-hour_initial',
                    'hepC_RNA',
                    'hepC_RNA-hour',
                    'hepC_RNA_initial',
                    'hepC_RNA-hour_initial',
                    'hepCRNA_log',
                    'hepCRNA_log-hour',
                    'hepCRNA_log_initial',
                    'hepCRNA_log-hour_initial',
                    'c_pnaIgA',
                    'c_pnaIgA-hour',
                    'c_pnaIgA_initial',
                    'c-pnaIgA-hour_iniital',
                    'specificGravity',
                    'specificGravity-hour',
                    'specificGravity_initial',
                    'specificGravity-hour_initial',
                    'pathologist',
                    'pathologist-hour',
                    'pathologist-hour_initial',
                    'pathologist_initial',
                    'timeFrozenResultCalled',
                    'timeFrozenResultCalled-hour',
                    'timeFrozenResultCalled_initial',
                    'timeFrozenResultCalled-hour_initial',
                    'resultsCalledTo',
                    'resultsCalledTo-hour',
                    'resultsCalledTo_initial',
                    'resultsCalledTo-hour_initial',
                    'calcitonin',
                    'calcitonin-hour',
                    'calcitonin_initial',
                    'calcitonin-hour_initial',
                    'Sodium, Feces',
                    'Sodium, Feces-hour',
                    'Sodium, Feces_initial',
                    'Sodium, Feces-hour_initial',
                    'Beta-2-Microglobulin',
                    'Beta-2-Microglobulin-hour',
                    'Beta-2-Microglobulin_initial',
                    'Beta-2-Microglobulin-hour_initial',




                    #new since December
                    'potassium',
                    'potassium-hour',
                    'potassium_initial',
                    'potassium-hour_initial',
                    'sodium',
                    'sodium-hour',
                    'sodium_initial',
                    'sodium-hour_initial',
                    'lipase',
                    'lipase-hour',
                    'lipase_initial',
                    'lipase-hour_initial',
                    'PaO2',
                    'PaO2-hour',
                    'PaO2_initial',
                    'PaO2-hour_initial',
                    'PvO2',
                    'PvO2-hour',
                    'PvO2_initial',
                    'PvO2-hour_initial',
                    'albumin',
                    'albumin-hour',
                    'albumin_initial',
                    'albumin-hour_initial',
                    'INR',
                    'INR-hour',
                    'INR_initial',
                    'INR-hour_initial',
                    'INR-hour_hs_initial',
                    'alk_phos',
                    'alk_phos-hour',
                    'alk_phos_initial',
                    'alk_phos-hour_initial',
                    'magnesium',
                    'magnesium-hour',
                    'magnesium_initial',
                    'magnesium-hour_initial',

                    'pH',
                    'pH-hour',
                    'pH_initial',
                    'pH-hour_initial',
                     ]


#short carry values -- vitals and a few labs (trop, ABG O2 values)
short_carry_cols=['O2device',
                 'O2device-hour',
                 'O2device_initial',
                 'O2device-hour_initial',

                 'SpO2',     # are we missing straight RR?
                 'SpO2-mean',
                 'SpO2-max',
                 'SpO2-min',
                 'SpO2-hour',
                 'SpO2_initial',
                 'SpO2-hour_initial',

                 'O2satABG',
                 'O2satABG-hour',

                 'SpO2/FiO2',
                 'SpO2/FiO2-mean',
                 'SpO2/FiO2-max',
                 'SpO2/FiO2-min',
                 'SpO2/FiO2_initial',
                 'SpO2/FiO2-hour_iniital',

                 'HEART_RT',
                 'HEART_RT-hour',
                 'HEART_RT-mean',
                 'HEART_RT-min',
                 'HEART_RT-max',
                 'HEART_RT_initial',
                 'HEART_RT-hour_initial',
                 
                 'HR',
                 'HR-hour',
                 'HR-mean',
                 'HR-min',
                 'HR-max',
                 'HR_initial',
                 'HR-hour_initial',
                 
                 'RR',
                 'RR-hour',
                 'RR-mean',
                 'RR-min',
                 'RR-max',
                 'RR_initial',
                 'RR-hour_initial',

                 'FiO2',
                 'FiO2-hour',
                 'FiO2_abg',
                 'FiO2_abg-hour',
                 'FiO2-mean',
                 'FiO2-max',
                 'FiO2-min',
                 'FiO2_initial',
                 'FiO2-hour_initial',

                 'BP_SYS',
                 'BP_SYS-hour',
                 'BP_SYS-mean',
                 'BP_SYS-min',
                 'BP_SYS-max',
                 'BP_SYS_initial',
                 'BP_SYS-hour_initial',

                 'BP_DIA',
                 'BP_DIA-hour',
                 'BP_DIA-mean',
                 'BP_DIA-min',
                 'BP_DIA-max',
                 'BP_DIA_initial',
                 'BP_DIA-hour_initial',
                 
                 'SBP',
                 'SBP-hour',
                 'SBP-mean',
                 'SBP-min',
                 'SBP-max',
                 'SBP_initial',
                 'SBP-hour_initial',

                 'DBP',
                 'DBP-hour',
                 'DBP-mean',
                 'DBP-min',
                 'DBP-max',
                 'DBP_initial',
                 'DBP-hour_initial',

                 'RESP_RT',
                 'RESP_RT-hour',
                 'RESP_RT-mean',
                 'RESP_RT-min',
                 'RESP_RT-max',
                 'RESP_RT_initial',
                 'RESP_RT-hour_initial',

                 'temp',
                 'temp-mean',
                 'temp-max',
                 'temp-min',
                 'temp-hour',
                 'temp_initial',
                 'temp-hour_initial',

                 'tropT_hs',
                 'tropT_hs-hour'
                 'tropT_hs_initial'
                 'tropT-hour_hs_initial'
                 ]

#indefinitely carry forward things that don't change over time
constant_cols=['COVID_pcr',
                'COVID_pcr-hour',
                'COVID_pcr_initial',
                'COVID_pcr-hour_initial',
                'COVID_tl',
                'COVID_tl-hour',
                'COVID_tl_initial',
                'COVID_tl-hour_initial',

                'height',
                'height-hour',
                'height_initial',
                'height-hour_initial',
                'Height',
                'Height-hour',
                'weight',
                'weight-hour',
                'weight_initial',
                'weight-hour_initial',
                'BMI',
                'BMI-hour',
                'BMI_initial',
                'BMI-hour_initial',
                'duration',


              ]

nonindex_cols=constant_cols+long_carry_cols+short_carry_cols
index_cols=['RECORD_ID', 'ENCNTR', 'hour', 'time_until_vent', 'time_since_vent']
all_cols=index_cols+nonindex_cols


#CHECK for dupicates in carry-forward column lists; raise errors
# IF there are duplicates, it will carry for double the rows which is not good
short_carry_cols = [x for x in short_carry_cols if x in df.columns]
long_carry_cols = [x for x in long_carry_cols if x in df.columns]
constant_cols = [x for x in constant_cols if x in df.columns]

shortcarry=pd.Series(short_carry_cols)
if shortcarry[shortcarry.duplicated()].size>0:
    raise ValueError('Duplicated column label(s) in short_carry_cols lists, must remove duplicates: '
                     +str(shortcarry[shortcarry.duplicated()]))

longcarry=pd.Series(long_carry_cols)
if shortcarry[longcarry.duplicated()].size>0:
    raise ValueError('Duplicated column label(s) in long_carry_cols lists, must remove duplicates: '
                     +str(longcarry[longcarry.duplicated()]))

const=pd.Series(constant_cols)
if const[const.duplicated()].size>0:
    raise ValueError('Duplicated column label(s) in constant_cols lists, must remove duplicates: '
                     +str(const[const.duplicated()]))

#CHECK if new columns that haven't been assigned to carry forward; raise error
# If no need to carry forward, can add to index_cols list

if df.columns[~df.columns.isin(all_cols)].size>0:
    raise ValueError('Missing Columns, please add to appropriate carry foward column list: '
          +str(df.columns[~df.columns.isin(all_cols)]))

#Now for loop to do the carry values forward
pts=df['RECORD_ID'].unique()  #unique record IDs to loop over
n=pts.size

for idx,pt in enumerate(pts):
    #for pt in pts:
    # select subdataframe of limit_long columns
    ix = df.index[df["RECORD_ID"]==pt]

    for col in short_carry_cols:
        temporary=df.loc[ix,col].fillna(method = "ffill",
                                    axis = 'rows',
                                    inplace = False,
                                    limit = limit_short)
        df.loc[ix,col] = temporary #because pandas slicing is weird, we must create
                                    # a new df and assign this back to subset of big df

    for col in long_carry_cols:
        temporary=df.loc[ix,col].fillna(method = "ffill",
                                    axis = 'rows',
                                    inplace = False,
                                    limit = limit_long)
        df.loc[ix,col] = temporary #because pandas slicing is weird, we must create
                                    # a new df and assign this back to subset of big df


    for col in constant_cols:
        temporary=df.loc[ix,col].fillna(method = "ffill",
                                    axis = 'rows',
                                    inplace = False,
                                    limit = None)
        df.loc[ix,col] = temporary #because pandas slicing is weird, we must create
                                    # a new df and assign this back to subset of big df

    #optionasl print statement - runs much slower with printing
    #print(pt)
    #print('{} of {} patients'.format(idx,n))

    #temporary = df.loc
    #temporary = df.loc[ix,long_carry_cols].fillna(method = "ffill",
    #                                                axis = 'rows',
    #                                                inplace = False,
    #                                                limit = limit_long)
    #df.loc[ix,long_carry_cols] = temporary #because pandas slicing is weird



    # select subdataframe of limit_short columns
    #df[pt,short_carry_cols].fillna(method="ffill", axis= 'rows', inplace=True,limit=limit_short)
    #temporary= df.loc[ix,short_carry_cols].fillna(method = "ffill",
#                                                    axis = 'rows',
#                                                    inplace = False,
#                                                    limit = limit_short)



#    df.loc[ix,long_carry_cols] = temporary
    # select subdataframe of indefinitely carried columns
    #df[pt,Indefinitely].fillna(method="ffill", axis= 'rows', inplace=True,limit=None)
#    temporary= df.loc[ix,Indefinitely].fillna(method = "ffill",
#                                                    axis = 'rows',
#                                                    inplace = False,
#                                                    limit = None)
    #df.loc[ix,long_carry_cols] = temporary

#save file
df.to_csv(fname+"_fillna.csv")
df.to_hdf(fname+"_fillna.hdf","fillna","w",complevel=6)
print('File saved to Output Directory')
