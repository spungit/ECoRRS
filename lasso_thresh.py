import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import Lasso
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc
import pickle

# out utilities will live here
from utils.utils import *

## Settings:
threshold = 10
alpha = 0.1

# set up markdown summary generator
directory = Directory()
ddir = directory.ddir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

lasso_dir = f'lasso_{threshold}/'
if not os.path.isdir(lasso_dir):
    os.makedirs(lasso_dir)

# setup markdown file output to report summary information
sfo = lasso_dir + f"lasso_summary_{threshold}_change_posthresh.md"
sw = Summary(sfo)

# LASSO : description
sw.wd("This workflow randomly splits data into a train and test set and performs LASSO. It then evaluates the performance.")


train_file = odir + f'covid_training_set-4_{threshold}.csv'
# data = pd.read_csv(train_file)
sw.wd(f'This was run with the file {train_file}, which removes rows that do not have at least {threshold} non-nan values')

# use current time to set seed, shuffle full set to make random
# dt = datetime.utcnow()
# unix_now = (dt - datetime(1970,1,1)).total_seconds()

for pt in np.linspace(12,168,14):
    sw.wd(f'pos_thresh = {pt}')
    # use data generator on train file
    data = data_gen(data_file = train_file, pos_thresh = pt)
    xtrain = data.xtrain
    ytrain = data.ytrain
    xtest = data.xtest
    ytest = data.ytest

    # train model
    sw.wd(f'alpha = {alpha}')
    reg = Lasso(alpha=alpha)
    reg.fit(xtrain,ytrain)

    # make predictions
    train_pred = reg.predict(xtrain)
    test_pred = reg.predict(xtest)

    # ROC analysis
    train_auc = roc_auc_score(ytrain,train_pred)
    test_auc = roc_auc_score(ytest,test_pred)

    sw.wd(f'Training AUC: {train_auc}')
    sw.wd(f'Test AUC : {test_auc}')

    # specficity sensitivity evaluation
    fpr,tpr,thresholds = roc_curve(ytrain,train_pred)
    spec_90 = (1-fpr[tpr > 0.90])[0]
    spec_95 = (1-fpr[tpr > 0.95])[0]
    spec_99 = (1-fpr[tpr > 0.99])[0]
    sw.wd(f'Training Specificity at 90 Sensitivity: {spec_90}')
    sw.wd(f'Training Specificity at 95 Sensitivity: {spec_95}')
    sw.wd(f'Training Specificity at 99 Sensitivity: {spec_99}')

    fpr,tpr,thresholds = roc_curve(ytest,test_pred)
    spec_90 = (1-fpr[tpr > 0.90])[0]
    spec_95 = (1-fpr[tpr > 0.95])[0]
    spec_99 = (1-fpr[tpr > 0.99])[0]
    sw.wd(f'Testing Specificity at 90 Sensitivity: {spec_90}')
    sw.wd(f'Testing Specificity at 95 Sensitivity: {spec_95}')
    sw.wd(f'Testing Specificity at 99 Sensitivity: {spec_99}')  

