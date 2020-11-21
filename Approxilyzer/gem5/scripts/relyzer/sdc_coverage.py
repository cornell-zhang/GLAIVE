#!/usr/bin/python


#AUTHOR: jiajia jiao
#Time: April,2020

import os
import sys
import numpy as np
import pandas as pd
import math

def get_critical_list(rate,infile,max_size,tp):
    a = np.loadtxt(infile)
    sort_index = np.lexsort(-a.T)
    sort_list = sort_index.tolist() 
    list_size = len(sort_list)
    #print(list_size)
    #print(sort_list) 
    cut_max = int(list_size * int(rate)/100.0)#math.ceil()
    
    #total cirtical list
    if (max_size < cut_max) :
	cut_max = max_size
    #print(cut_max)
   
    #same rank case
    if tp == 'fi':#or tp == 'opz':
    	for i in sort_list[cut_max:-1]:
		#print(a[sort_list[cut_max]])
		if a[sort_list[cut_max],1] == a[sort_list[cut_max-1],1] and a[sort_list[cut_max],2] == a[sort_list[cut_max-1],2] and a[sort_list[cut_max],3] == a[sort_list[cut_max-1],3]:
			cut_max = cut_max+1

    output=sort_list[:cut_max]
    
    return output

def get_all_critical_list(infile):
    a = np.loadtxt(infile)
    #print(a)
    a_new = a[~(a[:,1]==1.000000),:]
    sort_index = np.lexsort(-a_new.T)
    sort_list = sort_index.tolist()
    list_size = len(sort_list)
    #print('the max critical instructions are : ')
    #print(list_size)
    return list_size 
def comp_dis(infile):
    a = np.loadtxt(infile)
    #print(a)
    a_new = a[(a[:,1]==1.000000),:]
    sort_index = np.lexsort(-a_new.T)
    sort_list = sort_index.tolist()
    list_size1 = len(sort_list)
    print('the masked instructions are : %d'  % list_size1)
    a_new = a[(a[:,2]==1.000000),:]
    sort_index = np.lexsort(-a_new.T)
    sort_list = sort_index.tolist()
    list_size2 = len(sort_list)
    print('the SDC instructions are : %d '  % list_size2)
    a_new = a[(a[:,3]==1.000000),:]
    sort_index = np.lexsort(-a_new.T)
    sort_list = sort_index.tolist()
    list_size3 = len(sort_list)
    print('the Crash instructions are : %d '  % list_size3)
    



def comp_coverage(list1,list2):
    '''
    if (len(list1) != len(list2)):
        print('the wrong input lists for compute coverage \n')
        return -1
    else:
        list3 = list1+list2
        myset = set(list3)
        #return float(2*len(list1)-len(myset))/float(len(list1))
        return float(len(list1)+len(list2)-len(myset))/float(len(list2))
    ''' 
    list3 = list1+list2
    myset = set(list3)
    return float(len(list1)+len(list2)-len(myset))/float(len(list2))   

if len(sys.argv) < 0 or len(sys.argv) > 4:
	print ('Usage: python sdc_coverage.py [app_name] [rate]')
	exit()
app_name=sys.argv[1]
rate = sys.argv[2]
low = int(sys.argv[2])
high =int( sys.argv[3])
step = 5



approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + 'x86' + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name

infile_fi = app_prefix + '_inst_fi.sdclist'
infile_gl = app_prefix + '_inst_gl.sdclist'
infile_rf = app_prefix + '_inst_rf.sdclist'
infile_svm = app_prefix + '_inst_svm.sdclist'
infile_rf_bit = app_prefix + '_bit_rf.sdclist'
infile_mlpc_bit = app_prefix + '_bit_mlpc.sdclist'
comp_dis(infile_fi)
max_size = get_all_critical_list(infile_fi)
#max_size = 10000

for rate in range(low,high,step):
	#print(max_size)
	fi=get_critical_list(rate,infile_fi,max_size,'fi')
	gl=get_critical_list(rate,infile_gl,max_size,'opz')
	rf=get_critical_list(rate,infile_rf,max_size,'opz')
	svm=get_critical_list(rate,infile_svm,max_size,'opz')
	rf_bit=get_critical_list(rate,infile_rf_bit,max_size,'opz')
	mlpc_bit=get_critical_list(rate,infile_mlpc_bit,max_size,'opz')

	gl_coverage = comp_coverage(fi,gl)
	rf_coverage = comp_coverage(fi,rf)
	svm_coverage = comp_coverage(fi,svm)
	rf_bit_coverage = comp_coverage(fi,rf_bit)
	mlpc_bit_coverage = comp_coverage(fi,mlpc_bit)
	
	#print('\n the k vaulue is %d for rf_inst,svm_inst,rf_bit,mlp_bit and gl_bit' % rate)
	print('\n the k vaulue is %d for rf_inst,svm_inst,mlp_bit and gl_bit' % rate)
        print(rf_coverage)
        print(svm_coverage)
        #print(rf_bit_coverage)
        print(mlpc_bit_coverage)	
	print(gl_coverage)




	#print('the graph learning is %f \n' % gl_coverage)
	#print('the random forest at instruction level is %f \n' % rf_coverage)
	#print('the svm  at instruction level is %f \n' % svm_coverage)
	#print('the random forest at bit level  is %f \n' % rf_bit_coverage)
	#print('the mlpc at bit level  is %f \n' % mlpc_bit_coverage)
