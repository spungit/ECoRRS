import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import Lasso, LassoCV
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc
import pickle

# out utilities will live here
from utils.utils import *

## Settings:
threshold = 10
alpha = 0.1
col_select = ['FiO2','RBC_initial','SpO2-max','lymph#','mSOFA_initial','temp','weight']

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
sfo = lasso_dir + f"lasso_summary_{threshold}.md"
sw = Summary(sfo)

# LASSO : description
sw.wd("This workflow randomly splits data into a train and test set and performs LASSO. It then evaluates the performance.")


train_file = odir + f'covid_training_set-4_{threshold}.csv'
# data = pd.read_csv(train_file)
sw.wd(f'This was run with the file {train_file}, which removes rows that do not have at least {threshold} non-nan values')

# use current time to set seed, shuffle full set to make random
# dt = datetime.utcnow()
# unix_now = (dt - datetime(1970,1,1)).total_seconds()

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

# train model
sw.wd(f'alpha = {alpha}')
reg = Lasso(alpha=alpha)
# reg = LassoCV()
reg.fit(xtrain,ytrain)

# save model
save = {'model': reg, 'data' : data}
with open(lasso_dir + 'lasso_model.pkl', 'wb') as fid:
    pickle.dump(save, fid)

# make predictions
train_pred = reg.predict(xtrain)
test_pred = reg.predict(xtest)

# plot histogram of predictions colored by train/test and vent/no vent
plt.hist(train_pred[ytrain.values>0],label='train vent',bins=10,color='blue',density=True,alpha=0.4)
plt.hist(test_pred[ytest.values>0],label='test vent',bins=10,color='green',density=True,alpha=0.4)
plt.hist(train_pred[np.abs(ytrain.values-1)>0],label='train no vent',bins=10,color='red',density=True,alpha=0.4)
plt.hist(test_pred[np.abs(ytest.values-1)>0],label='test no vent',bins=10,color='orange',density=True,alpha=0.4)
plt.legend()
plt.title('LASSO Predictions')
plt.ylabel('Density')
plt.xlabel('$\hat y$')
plt.savefig(lasso_dir + 'lasso_hist.png')
sw.wi('lasso_hist.png')
plt.clf()
plt.close()
# plot histogram of predictions colored by train/test
plt.hist(train_pred,label='train',bins=10,color='purple',alpha=0.4)
plt.hist(test_pred,label='test',bins=10,color='yellow',alpha=0.4)
plt.legend()
plt.title('LASSO Predictions')
plt.ylabel('Number of Observations')
plt.xlabel('$\hat y$')
plt.savefig(lasso_dir + 'lasso_hist_traintest.png')
sw.wi('lasso_hist_traintest.png')
plt.clf()
plt.close()

# plot histogram of predictions colored by train vent/no vent
plt.hist(train_pred[ytrain.values>0],label='train vent',bins=10,color='blue',density=True,alpha=0.4)
plt.hist(train_pred[np.abs(ytrain.values-1)>0],label='train no vent',bins=10,color='red',density=True,alpha=0.4)
plt.legend()
plt.title('LASSO Predictions')
plt.ylabel('Density')
plt.xlabel('$\hat y$')
plt.savefig(lasso_dir + 'lasso_hist_train_ventnovent.png')
sw.wi('lasso_hist_train_ventnovent.png')
plt.clf()
plt.close()
# plot histogram of predictions colored by test and vent/no vent
plt.hist(test_pred[ytest.values>0],label='test vent',bins=10,color='green',density=True,alpha=0.4)
plt.hist(test_pred[np.abs(ytest.values-1)>0],label='test no vent',bins=10,color='orange',density=True,alpha=0.4)
plt.legend()
plt.title('LASSO Predictions')
plt.ylabel('Density')
plt.xlabel('$\hat y$')
plt.savefig(lasso_dir + 'lasso_hist_ventnovent.png')
sw.wi('lasso_hist_ventnovent.png')
plt.clf()
plt.close()

# ROC analysis
fpr,tpr,thresholds = roc_curve(ytrain,train_pred)
plt.plot(fpr,tpr,'r-',label='Training Data')
fpr,tpr,thresholds = roc_curve(ytest,test_pred)
plt.plot(fpr,tpr,'g-',label='Testing Data')
plt.xlim(0,1)
plt.ylim(0,1)
plt.title('LASSO ROC Curve')
plt.xlabel('1-Specificity')
plt.ylabel('Sensitivity')
plt.legend()

plt.savefig(lasso_dir + 'lasso_roc.png')
sw.wi('lasso_roc.png')
plt.clf()
plt.close()

train_auc = roc_auc_score(ytrain,train_pred)
test_auc = roc_auc_score(ytest,test_pred)

sw.wd(f'Training AUC: {train_auc}')
sw.wd(f'Test AUC : {test_auc}')

# specficity sensitivity evaluation
fpr,tpr,thresholds = roc_curve(ytrain,train_pred)
spec_90 = (1-fpr[tpr > 0.90])[0]
spec_80 = (1-fpr[tpr > 0.80])[0]
spec_75 = (1-fpr[tpr > 0.75])[0]
sw.wd(f'Training Specificity at 90 Sensitivity: {spec_90}')
sw.wd(f'Training Specificity at 80 Sensitivity: {spec_80}')
sw.wd(f'Training Specificity at 75 Sensitivity: {spec_75}')

fpr,tpr,thresholds = roc_curve(ytest,test_pred)
spec_90 = (1-fpr[tpr > 0.90])[0]
spec_80 = (1-fpr[tpr > 0.80])[0]
spec_75 = (1-fpr[tpr > 0.75])[0]
sw.wd(f'Testing Specificity at 90 Sensitivity: {spec_90}')
sw.wd(f'Testing Specificity at 80 Sensitivity: {spec_80}')
sw.wd(f'Testing Specificity at 75 Sensitivity: {spec_75}')


# PRC analysis
prec, rec, thresh = precision_recall_curve(ytrain, train_pred)
plt.plot(rec,prec,'r-',label='Training Data')
train_auprc = auc(rec, prec)
prec, rec, thresh = precision_recall_curve(ytest, test_pred)
test_auprc = auc(rec, prec)
plt.plot(rec,prec,'r-',label='Training Data')
plt.xlim(0,1)
plt.ylim(0,1)

#----- draw a diagonal line
plt.plot([0,1], [1,0], ls= "--", c= ".3")
plt.axes().set_aspect('equal')  #, 'datalim')
plt.title('LASSO Precision Recall Curve')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.legend()
plt.savefig(lasso_dir + 'lasso_prc.png')
sw.wi('lasso_prc.png')
plt.clf()
plt.close()

sw.wd(f'Training AUPRC: {train_auprc}')
sw.wd(f'Testing AUPRC: {test_auprc}')

train_auc = roc_auc_score(ytrain,train_pred)
test_auc = roc_auc_score(ytest,test_pred)

sw.wd(f'Training AUC: {train_auc}')
sw.wd(f'Test AUC : {test_auc}')

# print and plot all coefficient values
predictors = xtrain.columns
sw.wd('Predictors with coefficients:')
for pred, coef in zip(predictors, reg.coef_):
    sw.wd(f'{pred} : {coef}')

plt.figure(figsize=(12, 6))
plt.scatter(range(len(predictors)), reg.coef_)
plt.xticks(range(len(predictors)),predictors,rotation=45,ha='right',fontsize=20)
plt.title('Coefficient Values for each Predictor',fontsize=26)
ymax = np.max(reg.coef_) * 1.2
ymin = min([np.min(reg.coef_) * 1.2,-1e-4])
plt.ylim([ymin,ymax])
plt.ylabel('coefficient',fontsize=20)
plt.xlabel('predictors',fontsize=20)
plt.savefig(lasso_dir + 'lasso_coefs.png',bbox_inches='tight')
sw.wi('lasso_coefs.png')
plt.clf()
plt.close()

# plot just nonzero coefficients
nonzero_preds = predictors[np.where(reg.coef_ != 0)]
nonzero_coef = reg.coef_[np.where(reg.coef_ != 0)]
plt.figure(figsize=(12, 6))
plt.scatter(range(len(nonzero_preds)), nonzero_coef)
plt.xticks(range(len(nonzero_preds)),nonzero_preds,rotation=45,ha='right',fontsize=20)
plt.title('Non-zero Weights',fontsize=26)
plt.ylabel('Weight',fontsize=20)
plt.ylim([ymin,ymax])
plt.xlabel('Predictor',fontsize=20)
plt.savefig(lasso_dir + 'lasso_coefs_nonzero.png',bbox_inches='tight')
sw.wi('lasso_coefs_nonzero.png')
plt.clf()
plt.close()

