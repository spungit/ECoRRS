# ECoRRS Pipeline

## Data Processing
excel_to_csv.py : (run first only once in a folder synced to box) reads .xlsx source file and generates .csv files (on labs, clinicalevents, vitals sheets from excel file) 
*Notes: Hospital day and hour are since FIRST admission for that patient Enounter day and hour are since the MOST RECENT admission for that patient (admit date/time) Encounter column is the number of the encounter: 0 is pre-admission, 1 is first admission, 2 is second, etc. Gaps between admissions are labeled as part of the previous encounter. Discharge not used for hospital/encounter time calculations*

covid_combine.py : (run second) reads source .csv files and generates new "combined files in ./cleaned/withTimestamp Cleaned files from 'covid_clean.py' are concatenated into dataframe to generate the training set

covid_clean.py : (run third) reads source .csv files and generates new "cleaned files in ./cleaned/withTimestamp Convert all pseudo-numeric strings (>, <, ratios) to numeric Re-label O2 delivery devices

covid_gen.py : (run fourth) code which generates a raw training set from the COVID data.

carry_forward.py: (run fifth) carries forward vital sign values x12 hrs and lab values x72 hours.

covid_training_set.py : (run sixth) code that generates final training set after accounting for missing values.

## Modeling
