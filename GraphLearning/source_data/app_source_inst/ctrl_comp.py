import numpy as np
import networkx as nx
import os
import sys
import pprint as pp
test_app = sys.argv[1]

gl_dir = os.environ.get('GRAPHLEARN')
save_dir = gl_dir + '/source_data/app_source_inst/'
nodefile = save_dir + test_app +'nodelist'

ctrl_num=0
total_num=0
weight_num=0.0
with open(nodefile) as ff:
	for i, line in enumerate(ff):
		info = line.split()
		total_num=total_num+1
		if('test' in  info[1] or 'cmp' in info[1]  or 'ucomisd' in info[1] ):
			ctrl_num= ctrl_num + 1		
			weight_num = weight_num + float(info[5])

print('the ctrl_num is %d ' % ctrl_num)
print('the total_num is %d ' % total_num)
print('the weight_num is %f ' % weight_num)	




