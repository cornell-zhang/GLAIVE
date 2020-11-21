import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from datetime import datetime as dt
#import matplotlib.pyplot as plt
#from model.utils import draw_tree
#from model.metrics import *
np.random.seed(42)
import os
import sys
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss
from sklearn.metrics import roc_auc_score

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score



from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics

test_app = sys.argv[1]
def load_data():
    gl_dir = os.environ.get('GRAPHLEARN')
    data_dir = gl_dir + '/gdata'
    #data_dir = "path..../gdata"
    feat_data = np.load(("{}/"+test_app+"_feats.npy").format(data_dir))
    num_nodes = feat_data.shape[0]
    labels = np.empty((num_nodes,1), dtype=np.int64)
    train = []
    test  = []
    with open(("{}/"+test_app+"_labels.txt").format(data_dir)) as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            labels[int(info[0])] = int(info[1])
            if int(info[2]) == 1:
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

    y_train = y
    y_train = y_train.drop(test,axis=0)
    
    X_val = X
    X_val=X_val.drop(train,axis=0)

    y_val = y
    y_val = y_val.drop(train,axis=0)

    return X_train,X_val,y_train,y_val
print("before-load ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))   
data,target,train,test = load_data()    
X_train,X_val,y_train,y_val = get_train_val_static(data,target,train,test)





#rf = RandomForestClassifier(n_estimators=100,max_depth=4,bootstrap=False,min_samples_leaf=5)
print("after-load and before train ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
rf = RandomForestClassifier()
rf.fit(X_train,y_train)

rf_train_pred = rf.predict(X_train)
print("after-train and before predict ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))


rf_val_pred = rf.predict(X_val)
print("after-predict ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))

gl_dir = os.environ.get('GRAPHLEARN')
outfile_inst = gl_dir + '/sdc_output_ml_bit/'+test_app+'_rf'
#outfile_inst = 'path..../sdc_output_ml_bit/'+test_app+'_rf'
with open(outfile_inst,'w') as f:
    for num,i in enumerate(rf_val_pred):
        #if num < len(test):
        f.write('%d %d \n' % (test[num],i))


print('RandomForest-f1 score: %f' %f1_score(y_val,rf_val_pred, average="macro"))#,labels=[1]))
print('RandomForest-precision score: %f' %precision_score(y_val,rf_val_pred, average="micro"))#,labels=[1]))
print('RandomForest-recallscore: %f' %recall_score(y_val,rf_val_pred, average="micro"))#,labels=[1]))
print('RandomForest-test-accuracy score: %f' %accuracy_score(y_val,rf_val_pred, ))
print('RandomForest-train-accuracy score: %f' %accuracy_score(y_train,rf_train_pred, ))


print("MLPC for bit-level learning")
print(" before-train ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
from sklearn.neural_network import MLPClassifier
MLPC = MLPClassifier()
#MLPC = MLPClassifier(alpha=1, max_iter=1000)
MLPC.fit(X_train,y_train)
rf_train_pred = MLPC.predict(X_train)
print(" before-predict ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))

rf_val_pred = MLPC.predict(X_val)
print("after-train and before-predict ", dt.now().strftime("%m/%d/%Y %H:%M:%S"))

outfile_inst = gl_dir + '/sdc_output_ml_bit/'+test_app+'_mlpc'
#outfile_inst = 'path..../sdc_output_ml_bit/'+test_app+'_mlpc'
with open(outfile_inst,'w') as f:
    for num,i in enumerate(rf_val_pred):
        #if num < len(test):
        f.write('%d %d \n' % (test[num],i))


print('MLPC -f1 score: %f' %f1_score(y_val,rf_val_pred, average="macro"))#,labels=[1]))
print('MLPC -precision score: %f' %precision_score(y_val,rf_val_pred, average="micro"))#,labels=[1]))
print('MLPC -recallscore: %f' %recall_score(y_val,rf_val_pred, average="micro"))#,labels=[1]))
print('MLPC -accuracy score: %f' %accuracy_score(y_val,rf_val_pred, ))
print('MLPC-train-accuracy score: %f' %accuracy_score(y_train,rf_train_pred, ))


