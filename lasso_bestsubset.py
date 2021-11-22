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

# set up markdown summary generator
directory = Directory()
ddir = directory.ddir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

lasso_dir = f'lasso_bestsubset_{threshold}/'
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

# see which predictors show up the most often
N = 10
for s in range(N):
    print(s)
    # use data generator on train file
    data = data_gen(data_file = train_file, seed = s)
    xtrain = data.xtrain
    ytrain = data.ytrain
    xtest = data.xtest
    ytest = data.ytest
    predictors = xtrain.columns

    # train model
    reg = Lasso(alpha=alpha)
    #reg_cv = LassoCV(max_iter=500)
    
    reg.fit(xtrain,ytrain)
    #reg_cv.fit(xtrain,ytrain)
    #print(reg.n_iter_)
    #print(reg.dual_gap_)

    nonzero_preds = predictors[np.where(reg.coef_ != 0)]
    #nonzero_preds_cv = predictors[np.where(reg_cv.coef_ != 0)]

    if s == 0:
        full_list = nonzero_preds
    else:
        full_list = full_list.append(nonzero_preds)

# how often does each predictor get used in the model?
counts = np.asarray([(x,list(full_list).count(x)) for x in set(full_list)])
sort_idx = np.argsort(counts,axis=0)
counts = counts[sort_idx[:,0]]

cs = counts[:,1].astype(int)
ps = counts[:,0]

# plot predictor vs frequency
plt.figure(figsize=(12, 6))
plt.scatter(range(len(ps)), cs)
plt.xticks(range(len(ps)),ps,rotation=45,ha='right',fontsize=20)
plt.title('Frequency each Predictor is used by LASSO',fontsize=26)
plt.ylabel('Frequency in 100 trials',fontsize=20)
plt.xlabel('Predictor',fontsize=16)
plt.savefig(lasso_dir + 'pred_freq.png',bbox_inches='tight')
sw.wi('pred_freq.png')
plt.clf()
plt.close()
                                    
    
# save predictors
save = {'pred_counts': counts, 'preds': ps, 'counts': cs}
with open(lasso_dir + 'lasso_bestsubset.pkl', 'wb') as fid:
    pickle.dump(save, fid)

# use only selected predictors
preds = ps[cs > 0.5 * N]
xtrain = data.xtrain[preds]
xtest = data.xtest[preds]
# reg = Lasso(alpha=alpha)
reg = LassoCV()
reg.fit(xtrain,ytrain)

# make predictions
train_pred = reg.predict(xtrain)
test_pred = reg.predict(xtest)

# ROC analysis
train_auc = roc_auc_score(ytrain,train_pred)
test_auc = roc_auc_score(ytest,test_pred)

sw.wd(f'Training AUC: {train_auc}')
sw.wd(f'Test AUC : {test_auc}')

# print and plot all coefficient values
predictors = xtrain.columns

# plot just nonzero coefficients
# nonzero_preds = predictors[np.where(reg.coef_ != 0)]
# nonzero_coef = reg.coef_[np.where(reg.coef_ != 0)]
# sw.wd(f'{len(nonzero_preds)} non-zero coefficients:')
# sw.wd('Predictors with non-zero coefficients:')
for pred, coef in zip(preds, reg.coef_):
    sw.wd(f'{pred} : {coef}')

plt.figure(figsize=(12, 6))
plt.scatter(range(len(preds)), reg.coef_)
plt.xticks(range(len(preds)),preds,rotation=45,ha='right',fontsize=20)
plt.title('Coefficient Values for each Predictor',fontsize=26)
ymax = np.max(reg.coef_) * 1.1
ymin = min([np.min(reg.coef_) * 1.1,-1e-4])
plt.ylim([ymin,ymax])
plt.ylabel('coefficient',fontsize=20)
plt.xlabel('predictors',fontsize=20)
plt.savefig(lasso_dir + 'lasso_coefs.png',bbox_inches='tight')
sw.wi('lasso_coefs.png')
plt.clf()
plt.close()

adj_train_auc = np.zeros(len(preds))
adj_test_auc = np.zeros(len(preds))
# see how results would change removing some
for idx, pred in enumerate(preds):
    sw.wd(f'Removing {pred}:')

    # temporarily store value of coef, then set to 0
    rem = reg.coef_[np.where(predictors==pred)]
    reg.coef_[np.where(predictors==pred)] = 0

    # make predictions
    train_pred = reg.predict(xtrain)
    test_pred = reg.predict(xtest)
    
    # ROC analysis
    adj_train_auc[idx] = roc_auc_score(ytrain,train_pred)
    adj_test_auc[idx] = roc_auc_score(ytest,test_pred)

    sw.wd(f'Training AUC with {pred} removed: {adj_train_auc[idx]}')
    sw.wd(f'Test AUC with {pred} removed: {adj_test_auc[idx]}')

    # replace the removed predictor
    reg.coef_[np.where(predictors==pred)] = rem


# plot train adjusted AUCs
ymax = train_auc * 1.05
ymin = test_auc * 0.95
plt.figure(figsize=(12, 6))
plt.scatter(range(len(preds)), adj_train_auc)
plt.plot([-20,20],[train_auc, train_auc],'k--',label='Baseline Train AUC')
plt.xticks(range(len(preds)),preds,rotation=45,ha='right',fontsize=20)
plt.title('Train AUC with Predictors Removed',fontsize=26)
plt.ylabel('AUC',fontsize=20)
plt.ylim(np.percentile(adj_train_auc, (0,100))+[-0.001, 0.001])
plt.xlim([-1,len(preds)])
plt.xlabel('Predictor Removed',fontsize=20)
plt.legend(fontsize=20)
plt.savefig(lasso_dir + 'train_adj_auc.png',bbox_inches='tight')
sw.wi('train_adj_auc.png')
plt.clf()
plt.close()

# plot test adjusted AUCs
plt.figure(figsize=(12, 6))
plt.scatter(range(len(preds)), adj_test_auc)
plt.plot([-20,20],[test_auc, test_auc],'k--',label='Baseline Test AUC')
plt.xticks(range(len(preds)),preds,rotation=45,ha='right',fontsize=20)
plt.title('Test AUC with Predictors Removed',fontsize=26)
plt.ylabel('AUC',fontsize=20)
plt.ylim(np.percentile(adj_test_auc, (0,100))+[-0.001, 0.001])
plt.xlim([-1,len(preds)])
plt.xlabel('Predictor Removed',fontsize=20)
plt.legend(fontsize=20)
plt.savefig(lasso_dir + 'test_adj_auc.png',bbox_inches='tight')
sw.wi('test_adj_auc.png')
plt.clf()
plt.close()
