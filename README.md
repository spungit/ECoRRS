# ECoRRS Pipeline

## Data Processing
`excel_to_csv.py` : (run first only once in a folder synced to box) reads .xlsx source file and generates .csv files (on labs, clinicalevents, vitals sheets from excel file) 
*Notes: Hospital day and hour are since FIRST admission for that patient Enounter day and hour are since the MOST RECENT admission for that patient (admit date/time) Encounter column is the number of the encounter: 0 is pre-admission, 1 is first admission, 2 is second, etc. Gaps between admissions are labeled as part of the previous encounter. Discharge not used for hospital/encounter time calculations*

`covid_combine.py` : (run second) reads source .csv files and generates new "combined files in ./cleaned/withTimestamp Cleaned files from 'covid_clean.py' are concatenated into dataframe to generate the training set

`covid_clean.py` : (run third) reads source .csv files and generates new "cleaned files in ./cleaned/withTimestamp Convert all pseudo-numeric strings (>, <, ratios) to numeric Re-label O2 delivery devices

`covid_gen.py` : (run fourth) code which generates a raw training set from the COVID data.

`carry_forward.py` : (run fifth) carries forward vital sign values x12 hrs and lab values x72 hours.

`covid_training_set.py` : (run sixth) code that generates final training set after accounting for missing values.

## Modeling--LASSO
`lasso_thresh.py`: (optional) Our workflow marks patients as
"positive" if they were put on a ventilator within a certain amount of
time of the current observation. `lasso_thresh.py` runs LASSO with
different values of this time threshold to see how sensitive the model
is to changes in the threshold. 

`lasso_test_alpha.py`: (reocmmended) This script evaluates different
LASSO parameters (alpha) to help make an informed decision on
regularization. This is an important step to choose an alpha parameter
that promotes sparsity while not sacrificing performance. 

`lasso_bestsubset.py`: (recommended) this script runs LASSO many times
with different randomized training/testing splits to identify which
predictors are included into the model the most. It identifies the
most commonly used predictors, and evaluates how removing these
predictors would affect the model. This is an important step to make
an informed decision of which predictors to use to promote a sparse
model. 

`lasso.py`: Once parameters and predictors have been chosen, run this
to generate a LASSO model and evaluate performance on a test set. 

`bootstrap_lasso.py`: Once the LASSO model has been created by
`lasso.py`, run this script to generate bootstrapped statistics for
performance and ROC curves with confidence bands. 


## Modeling--XGBoost


## Utils
`utils.py`: where all helper functions utilized by our workflow live

