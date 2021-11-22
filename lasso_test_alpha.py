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
#col_select = ['FiO2','RBC_initial','SpO2-max','lymph#','mSOFA_initial','temp','weight']
col_select = None
alphas = np.logspace(-3,0,20)
#alphas = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 5e-1]

# set up markdown summary generator
directory = Directory()
ddir = directory.ddir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

lasso_dir = f'lasso_{threshold}_alphatest/'
if not os.path.isdir(lasso_dir):
    os.makedirs(lasso_dir)

# setup markdown file output to report summary information
sfo = lasso_dir + f"lasso_summary_{threshold}_alphatest.md"
sw = Summary(sfo)

# LASSO : description
sw.wd("This workflow randomly splits data into a train and test set and performs LASSO. It then tests different values of lambda")


train_file = odir + f'covid_training_set-4_{threshold}.csv'
data = pd.read_csv(train_file)
sw.wd(f'This was run with the file {train_file}, which removes rows that do not have at least {threshold} non-nan values')

# use data generator on train file
data = data_gen(data_file = train_file)
ytrain = data.ytrain
ytest = data.ytest

if col_select is not None:
    xtest = data.xtest[col_select]
    xtrain = data.xtrain[col_select]
else:
    xtest = data.xtest
    xtrain = data.xtrain

predictors = xtrain.columns

aucs = np.zeros(len(alphas))
specs = np.zeros(len(alphas))
nonzeros = np.zeros(len(alphas))
for idx, alpha in enumerate(alphas):
    # train model
    sw.wd(f'alpha = {alpha}')
    reg = Lasso(alpha=alpha)
    reg.fit(xtrain,ytrain)

    # make predictions
    train_pred = reg.predict(xtrain)
    test_pred = reg.predict(xtest)

    train_auc = roc_auc_score(ytrain,train_pred)
    test_auc = roc_auc_score(ytest,test_pred)
    aucs[idx] = test_auc

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
    specs[idx] = spec_90


    # PRC analysis
    prec, rec, thresh = precision_recall_curve(ytrain, train_pred)
    train_auprc = auc(rec, prec)
    prec, rec, thresh = precision_recall_curve(ytest, test_pred)
    test_auprc = auc(rec, prec)

    sw.wd(f'Training AUPRC: {train_auprc}')
    sw.wd(f'Testing AUPRC: {test_auprc}')

    # plot just nonzero coefficients
    nonzero_preds = predictors[np.where(reg.coef_ != 0)]
    nonzeros[idx] = len(nonzero_preds)
    sw.wd(f'Total number of nonzero weights: {len(nonzero_preds)}')




# aucs
ax = plt.gca()
plt.plot(alphas,aucs)
plt.title(r'AUCs for different values of $\alpha$',fontsize=18)
plt.xlabel(r'$\alpha$',fontsize=14)
plt.ylabel('AUC',fontsize=14)
ax.set_xscale('log')
plt.ylim([0,1])
plt.savefig(lasso_dir + 'test_aucs.png',bbox_inches='tight')
sw.wi('test_aucs.png')
plt.clf()
plt.close()


# specs
ax = plt.gca()
plt.plot(alphas,specs)
plt.title('Specificity at 90% Sensitivity',fontsize=18)
plt.xlabel(r'$\alpha$',fontsize=14)
plt.ylabel('Specificity',fontsize=14)
ax.set_xscale('log')
plt.ylim([-0.01,1])
plt.savefig(lasso_dir + 'test_specs.png',bbox_inches='tight')
sw.wi('test_specs.png')
plt.clf()
plt.close()

# nonzeros
ax = plt.gca()
plt.plot(alphas,nonzeros)
plt.title('Number of Nonzero Weights',fontsize=18)
plt.xlabel(r'$\alpha$',fontsize=14)
plt.ylabel('Nonzero Weights',fontsize=14)
ax.set_xscale('log')
plt.savefig(lasso_dir + 'test_weights.png',bbox_inches='tight')
sw.wi('test_weights.png')
plt.clf()
plt.close()
