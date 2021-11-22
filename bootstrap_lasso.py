import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import Lasso
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc
import pickle
import pdb
# out utilities will live here
from utils.utils import *


## Settings that change:
threshold = 10
trials = 1000
col_select = ['FiO2','RBC_initial','SpO2-max','lymph#','mSOFA_initial','temp','weight']

# set up markdown summary generator
directory = Directory()
ddir = directory.ddir
odir = directory.odir
print("  Data Directory (ddir): {}".format(ddir))
print("Output Directory (odir): {}".format(odir))

lasso_dir = f'bootstrap_lasso_{threshold}/'
if not os.path.isdir(lasso_dir):
    os.makedirs(lasso_dir)

# setup markdown file output to report summary information
sfo = lasso_dir + f"bootstrap_lasso_summary_{threshold}.md"
sw = Summary(sfo)

# LASSO : description

sw.wd("This workflow performs bootstrap analysis with a LASSO regression model")
text = f"We will train our model on 80% of available data, test ig on the remaining 20%. "
text += f"Then sample our testing set {trials} times with replacement to provide "
text += f"confidence bounds for our estimates."
sw.wd(text)


# load lasso stuff from file
with open(f'lasso_{threshold}/lasso_model.pkl','rb') as fid:
    data = pickle.load(fid)

train = data['data'].train
test = data['data'].test
xtrain = data['data'].xtrain
ytrain = data['data'].ytrain
xtest = data['data'].xtest
ytest = data['data'].ytest

if col_select is not None:
    xtest = data['data'].xtest[col_select]
    xtrain = data['data'].xtrain[col_select]
else:
    xtest = data['data'].xtest
    xtrain = data['data'].xtrain

reg = data['model']
predictors = xtrain.columns

# make predictions on training/testing set
train_pred = reg.predict(xtrain)
test_pred = reg.predict(xtest)

# train roc analysis
fpr,tpr,thresholds = roc_curve(ytrain,train_pred)
plt.plot(fpr,tpr,'r-',label='Training Data')
plt.xlim(0,1)
plt.ylim(0,1)
#----- draw a diagonal line
plt.plot([0,1], [0,1], ls= "--", c= ".3")
plt.axes().set_aspect('equal')  #, 'datalim')
plt.title('LASSO ROC Curve Training Set',fontsize=18)
plt.xlabel('1-Specificity',fontsize=14)
plt.ylabel('Sensitivity',fontsize=14)
plt.legend()
plt.savefig(lasso_dir + 'lasso_roc_train.png')
sw.wi('lasso_roc_train.png')
plt.clf()
plt.close()

train_auc = roc_auc_score(ytrain,train_pred)
spec_90 = (1-fpr[tpr > 0.90])[0]
spec_80 = (1-fpr[tpr > 0.80])[0]
spec_75 = (1-fpr[tpr > 0.75])[0]

sw.wd(f'Training AUROC: {train_auc}')
sw.wd(f'Training Specificity at 90 Sensitivity: {spec_90}')
sw.wd(f'Training Specificity at 80 Sensitivity: {spec_80}')
sw.wd(f'Training Specificity at 75 Sensitivity: {spec_75}')

# train prc analysis
prec, rec, thresh = precision_recall_curve(ytrain, train_pred)
plt.plot(rec,prec,'r-',label='Training Data')
plt.xlim(0,1)
plt.ylim(0,1)
#----- draw a diagonal line
plt.plot([0,1], [1,0], ls= "--", c= ".3")
plt.axes().set_aspect('equal')  #, 'datalim')
plt.title('LASSO Precision Recall Curve Training Set',fontsize=18)
plt.xlabel('Recall',fontsize=14)
plt.ylabel('Precision',fontsize=14)
plt.legend()
plt.savefig(lasso_dir + 'lasso_prc_train.png')
sw.wi('lasso_prc_train.png')
plt.clf()
plt.close()
train_auprc = auc(rec, prec)
sw.wd(f'Training AUPRC: {train_auprc}')

# test roc and prc point estimates
fpr_og, tpr_og, thresholds = roc_curve(ytest,test_pred)
test_auc = roc_auc_score(ytest,test_pred)
sw.wd(f'Test AUROC: {test_auc}')
spec_90 = (1-fpr_og[tpr_og >= 0.90])[0]
spec_80 = (1-fpr_og[tpr_og >= 0.80])[0]
spec_75 = (1-fpr_og[tpr_og >= 0.75])[0]
thresh_75 = thresholds[tpr_og >= 0.75][0]

# calculate ppv, npv
ep = 1e-8
tp_og = tpr_og * (sum(ytest))
tn_og = (1 - fpr_og) * (len(ytest)-sum(ytest))
fp_og = tn_og / (1-fpr_og+ep) - tn_og
fn_og = tp_og / (tpr_og+ep) - tp_og

ppv_og = tp_og / (tp_og + fp_og + ep)
npv_og = tn_og / (tn_og + fn_og + ep)

ppv_75 = ppv_og[tpr_og >= 0.75][0]
ppv_90 = ppv_og[tpr_og >= 0.90][0]
npv_75 = npv_og[tpr_og >= 0.75][0]
npv_90 = npv_og[tpr_og >= 0.90][0]

# raw tp, tn, fp, fn at 75% sensitivity
tp_75 = tp_og[tpr_og >= 0.75][0]
tn_75 = tn_og[tpr_og >= 0.75][0]
fp_75 = fp_og[tpr_og >= 0.75][0]
fn_75 = fn_og[tpr_og >= 0.75][0]

prec_og, rec_og, thresh = precision_recall_curve(ytest, test_pred)
test_auprc = auc(rec, prec)
sw.wd(f'Test AUPRC: {test_auprc}')

# initialize boostrap metrics
aucs = np.zeros(trials)
auprcs = np.zeros(trials)
spec_90_arr = np.zeros(trials)
spec_80_arr = np.zeros(trials)
spec_75_arr = np.zeros(trials)
ppv_75_arr = np.zeros(trials)
npv_75_arr = np.zeros(trials)
ppv_90_arr = np.zeros(trials)
npv_90_arr = np.zeros(trials)
tp_75_arr = np.zeros(trials)
tn_75_arr = np.zeros(trials)
fp_75_arr = np.zeros(trials)
fn_75_arr = np.zeros(trials)
thresh_75_arr = np.zeros(trials)

#fpr_arr = np.zeros([len(fpr_og), trials])
#tpr_arr = np.zeros([len(tpr_og), trials])

# now let's bootstrap
for i in range(trials):
    test_subset = test.sample(frac=1,replace=True)
    x_bs = test_subset[predictors]
    y_bs = test_subset['vent']

    # make predictions
    bs_pred = reg.predict(x_bs)

    # # ROC analysis
    fpr, tpr, thresholds = roc_curve(y_bs, bs_pred)
    spec_90_arr[i] =  (1-fpr[tpr >= 0.90])[0] - spec_90
    spec_80_arr[i] =  (1-fpr[tpr >= 0.80])[0] - spec_80
    spec_75_arr[i] =  (1-fpr[tpr >= 0.75])[0] - spec_75
    thresh_75_arr[i] = thresholds[tpr >= 0.75][0] - thresh_75
    aucs[i] = roc_auc_score(y_bs, bs_pred) - test_auc

    # PRC analysis
    prec, rec, thresh = precision_recall_curve(ytest,test_pred)
    auprcs[i] = auc(rec, prec)

    # ppv, npv
    tp = tpr * (sum(y_bs))
    tn = (1 - fpr) * (len(y_bs)-sum(y_bs))
    fp = tn / (1-fpr+ep) - tn 
    fn = tp / (tpr+ep) - tp

    ppv = tp / (tp + fp + ep)
    npv = tn / (tn + fn + ep)

    tp_75_arr[i] = tp[tpr >= 0.75][0] - tp_75
    tn_75_arr[i] = tn[tpr >= 0.75][0] - tn_75
    fp_75_arr[i] = fp[tpr >= 0.75][0] - fp_75
    fn_75_arr[i] = fn[tpr >= 0.75][0] - fn_75
    
    ppv_75_arr[i] = ppv[tpr >= 0.75][0] - ppv_75
    ppv_90_arr[i] = ppv[tpr >= 0.90][0] - ppv_90
    npv_75_arr[i] = npv[tpr >= 0.75][0] - npv_75
    npv_90_arr[i] = npv[tpr >= 0.90][0] - npv_90

    if i % 100 == 0:
        print(i)


test_auc_ci = [test_auc-np.percentile(aucs,97.5), test_auc-np.percentile(aucs,2.5)]
#test_auc_ci = [np.percentile(aucs,5), np.percentile(aucs,95)]
sw.wd(f'Testing AUROC 95% CI: ({np.round(test_auc_ci[0],3)},{np.round(test_auc_ci[1],3)})')

thresh_75_ci = [thresh_75-np.percentile(thresh_75_arr,97.5), thresh_75-np.percentile(thresh_75_arr,2.5)]
sw.wd(f'Decision threshold 95% CI: ({np.round(thresh_75_ci[0],3)},{np.round(thresh_75_ci[1],3)})')

test_auprc_ci = [test_auprc-np.percentile(auprcs,97.5), test_auprc-np.percentile(auprcs,2.5)]
sw.wd(f'Testing AUPRC 95% CI: ({np.round(test_auprc_ci[0],3)},{np.round(test_auprc_ci[1],3)})')

spec_90_ci = [spec_90-np.percentile(spec_90_arr,97.5), spec_90-np.percentile(spec_90_arr,2.5)] 
#spec_90_ci = [np.percentile(spec_90_arr,5), np.percentile(spec_90_arr,95)] 
sw.wd(f'Specificity at 90% sensitivity 95% CI: ({np.round(spec_90_ci[0],3)},{np.round(spec_90_ci[1],3)})')

spec_80_ci = [spec_80-np.percentile(spec_80_arr,97.5), spec_80-np.percentile(spec_80_arr,2.5)] 
#spec_80_ci = [np.percentile(spec_80_arr,5), np.percentile(spec_80_arr,80)] 
sw.wd(f'Specificity at 80% sensitivity 95% CI: ({np.round(spec_80_ci[0],3)},{np.round(spec_80_ci[1],3)})')

spec_75_ci = [spec_75-np.percentile(spec_75_arr,97.5), spec_75-np.percentile(spec_75_arr,2.5)] 
#spec_75_ci = [np.percentile(spec_75_arr,5), np.percentile(spec_75_arr,80)] 
sw.wd(f'Specificity at 75% sensitivity 80% CI: ({np.round(spec_75_ci[0],3)},{np.round(spec_75_ci[1],3)})')


ppv_75_ci = [ppv_75-np.percentile(ppv_75_arr,97.5), ppv_75 - np.percentile(ppv_75_arr,2.5)] 
sw.wd(f'PPV at 75% sensitivity 95% CI: ({np.round(ppv_75_ci[0],3)},{np.round(ppv_75_ci[1],3)})')
ppv_90_ci = [ppv_90-np.percentile(ppv_90_arr,97.5), ppv_90 - np.percentile(ppv_90_arr,2.5)] 
sw.wd(f'PPV at 90% sensitivity 95% CI: ({np.round(ppv_90_ci[0],3)},{np.round(ppv_90_ci[1],3)})')

npv_75_ci = [npv_75-np.percentile(npv_75_arr,97.5), npv_75 - np.percentile(npv_75_arr,2.5)] 
sw.wd(f'NPV at 75% sensitivity 95% CI: ({np.round(npv_75_ci[0],3)},{np.round(npv_75_ci[1],3)})')
npv_90_ci = [npv_90-np.percentile(npv_90_arr,97.5), npv_90 - np.percentile(npv_90_arr,2.5)] 
sw.wd(f'NPV at 90% sensitivity 95% CI: ({np.round(npv_90_ci[0],3)},{np.round(npv_90_ci[1],3)})')


tp_75_ci = [tp_75-np.percentile(tp_75_arr,97.5), tp_75 - np.percentile(tp_75_arr,2.5)] 
sw.wd(f'# of TPs at 75% sensitivity 95% CI: ({np.round(tp_75_ci[0],3)},{np.round(tp_75_ci[1],3)})')

tn_75_ci = [tn_75-np.percentile(tn_75_arr,97.5), tn_75 - np.percentile(tn_75_arr,2.5)] 
sw.wd(f'# of TNs at 75% sensitivity 95% CI: ({np.round(tn_75_ci[0],3)},{np.round(tn_75_ci[1],3)})')

fp_75_ci = [fp_75-np.percentile(fp_75_arr,97.5), fp_75 - np.percentile(fp_75_arr,2.5)] 
sw.wd(f'# of FPs at 75% sensitivity 95% CI: ({np.round(fp_75_ci[0],3)},{np.round(fp_75_ci[1],3)})')

fn_75_ci = [fn_75-np.percentile(fn_75_arr,97.5), fn_75 - np.percentile(fn_75_arr,2.5)] 
sw.wd(f'# of FNs at 75% sensitivity 95% CI: ({np.round(fn_75_ci[0],3)},{np.round(fn_75_ci[1],3)})')

# SJR method for ROC
tp = tpr_og * (sum(ytest))
tn = (1 - fpr_og) * (len(ytest)-sum(ytest))

ub_fpr = []
ub_tpr = []
lb_fpr = []
lb_tpr = []
for i in range(len(tp)):
    if tp[i] > 35 and tn[i] > 35:
        # if samples are > 35, then we can use SJR method from macskassy
        d = 1.36 / np.sqrt(tp[i]) # this is counter intuitive, but what the paper says
        e = 1.36 / np.sqrt(tn[i])

        ub_fpr += [fpr_og[i] + d]  # upper bound x-values
        ub_tpr += [tpr_og[i] + e]  # upper bound y-values
        lb_fpr += [fpr_og[i] - d]  # lower bound x-values
        lb_tpr += [tpr_og[i] - e]  # lower bound y-values


# SJR for PRC--need to do separately in case arrays are different sizes which is annoying
tp = rec_og * (sum(ytest))

ub_prec = []
lb_prec = []
ub_rec = []
lb_rec = []
for i in range(len(tp)):
    if tp[i] > 35:
        # if samples are > 35, then we can use SJR method from macskassy
        d = 1.36 / np.sqrt(tp[i]) 

        ub_prec += [prec_og[i] + d]
        lb_prec += [prec_og[i] - d]
        ub_rec += [rec_og[i] + d]
        lb_rec += [rec_og[i] - d]

#----- plot SJR
#plt.figure(figsize=(9,6))
ax = plt.gca()
ax.set_aspect('equal')  #, 'datalim')
title= 'ROC with 95% C.I.'
#title+= '\n${}$% Median Specificity at 75% Sensitivity'.format(np.round(median_spc*100,3))
plt.plot(fpr_og, tpr_og, 'k-')
plt.plot(ub_fpr, ub_tpr, 'c--')
plt.plot(lb_fpr, lb_tpr, 'c--')
plt.plot([0,1], [0,1], ls= "--", c= ".3")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.title(title,fontsize=18)
plt.xlabel('1-Specificity',fontsize=14)
plt.ylabel('Sensitivity',fontsize=14)
plt.savefig(lasso_dir + 'lasso_roc_test_sjr.png')
sw.wi('lasso_roc_test_sjr.png')
plt.clf()
plt.close()


#----- plot PRC
#plt.figure(figsize=(9,6))
ax = plt.gca()
ax.set_aspect('equal')  #, 'datalim')
title= 'PRC with 95% C.I.'
#title+= '\n${}$% Median Specificity at 75% Sensitivity'.format(np.round(median_spc*100,3))
plt.plot(rec_og, prec_og, 'k-')
plt.plot(ub_rec, ub_prec, 'c--')
plt.plot(lb_rec, lb_prec, 'c--')
plt.plot([0,1], [1,0], ls= "--", c= ".3")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.title(title,fontsize=18)
plt.xlabel('Recall',fontsize=14)
plt.ylabel('Precision',fontsize=14)
plt.savefig(lasso_dir + 'lasso_prc_test_sjr.png')
sw.wi('lasso_prc_test_sjr.png')
plt.clf()
plt.close()

