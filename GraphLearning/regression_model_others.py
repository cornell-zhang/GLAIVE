import pandas as pd
import numpy as np
from sklearn.utils import shuffle
import os
import sys
#import matplotlib.pyplot as plt
#from model.utils import draw_tree
#from model.metrics import *
np.random.seed(42)

from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss
from sklearn.metrics import roc_auc_score

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn import metrics

from datetime import datetime as dat
test_app = sys.argv[1]

def load_data():
    gl_dir = os.environ.get('GRAPHLEARN')
    data_dir = gl_dir +'/gdata'
    feat_data = np.load(("{}/" + test_app+"_feats.npy").format(data_dir))
    num_nodes = feat_data.shape[0]
    labels = np.empty((num_nodes,3), dtype=np.float64)
    train = []
    test  = []
    #with open("{}/lu_cb_inst_labels.txt".format(data_dir)) as fp:
    with open(("{}/"+test_app+"_labels.txt").format(data_dir)) as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            labels[int(info[0])] = info[1:4]
            if int(info[4]) == 1:
                train.append(int(info[0]))
            else:
                test.append(int(info[0]))
    feat_data = pd.DataFrame(feat_data)
    labels = pd.DataFrame(labels)
    
    return feat_data, labels, train, test


from sklearn.model_selection import train_test_split
def get_train_val(X,y):
    X_train,X_val,y_train,y_val =  train_test_split(X, y, test_size=0.25, random_state=42)
    return X_train.reset_index(drop=True),X_val.reset_index(drop=True),y_train,y_val
   
def get_train_val_static(X,y,train,test): 
    X_train = X
    X_train=X_train.drop(test,axis=0)
    print(len(X_train))

    y_train = y
    y_train = y_train.drop(test,axis=0)
    print(len(y_train))
    
    X_val = X
    X_val=X_val.drop(train,axis=0)
    print(len(X_val))
    
    y_val = y
    y_val = y_val.drop(train,axis=0)
    print(len(y_val))
    return X_train,X_val,y_train,y_val
print("before-load-time stamp:", dat.now().strftime("%m/%d/%Y %H:%M:%S"))
data,target,train,test = load_data()    
X_train,X_val,y_train,y_val = get_train_val_static(data,target,train,test)

gl_dir = os.environ.get('GRAPHLEARN')

#rf = RandomForestClassifier(n_estimators=100,max_depth=4,bootstrap=False,min_samples_leaf=5)
rf = RandomForestRegressor()
rf.fit(X_train,y_train)

rf_train_pred = rf.predict(X_train)
rf_val_pred = rf.predict(X_val)
print("random forest")
print("after-predict-time stamp:", dat.now().strftime("%m/%d/%Y %H:%M:%S"))
print('random forest regressor \n')
print(r2_score(y_val,rf_val_pred))
print(mean_squared_error(y_val,rf_val_pred))
print(mean_absolute_error(y_val,rf_val_pred))
outfile_inst = gl_dir + '/sdc_output_classic/'+test_app+'_rf'
with open(outfile_inst,'w') as f:
    for num,i in enumerate(rf_val_pred):
	total= i[0]+i[1]+i[2]
        f.write('%d  %f  %f  %f  \n' % (test[num],i[0]/total,i[1]/total,i[2]/total))


from sklearn import linear_model
from sklearn.svm import LinearSVR
from sklearn.multioutput import MultiOutputRegressor
print("support vector machine")
svm = LinearSVR(C=10)
wrapper = MultiOutputRegressor(svm )
#kernel='linear'
#kernel='rbf' 
#kernel='sigmoid'
#kernel='poly', degree=8
wrapper.fit(X_train, y_train)
#svm.fit(X_train,y_train)
rf_train_pred = wrapper.predict(X_train)
rf_val_pred = wrapper.predict(X_val)
print("after-predict-time stamp:", dat.now().strftime("%m/%d/%Y %H:%M:%S"))
print('SV regressor \n')
print(r2_score(y_val,rf_val_pred))
print(mean_squared_error(y_val,rf_val_pred))
print(mean_absolute_error(y_val,rf_val_pred))
outfile_inst = gl_dir + '/sdc_output_classic/'+test_app+'_svm'
with open(outfile_inst,'w') as f:
    for num,i in enumerate(rf_val_pred):
        total= i[0]+i[1]+i[2]
        f.write('%d  %f  %f  %f  \n' % (test[num],i[0]/total,i[1]/total,i[2]/total))

