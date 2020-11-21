#!/usr/bin/python

# generate the simple output for test

import os
import sys

if len(sys.argv)!= 3:
	print ('Usage: python inst_dep_gen.py [app_name] [isa]')
	exit()
app_name=sys.argv[1]
isa = sys.argv[2]

approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name
infile = app_prefix + '_def_use.txt'
infile_str = app_prefix + '_dependent_stores.txt'
outfile = app_prefix + '_dep.txt'


output=[]
db_info = [i for i in open(infile).read().splitlines()[1:]]
db_info_str = [i for i in open(infile_str).read().splitlines()[1:]]
#def-use dep
for pc_dep in db_info:
    pc = pc_dep.split(' ')[0]
    pc_list_raw = pc_dep.split(' ')[2:]
    #store-load dep
    
    for pc_str in db_info_str:
        if(pc_str.split(' ')[0] == pc):
            pc_list_raw.append(pc_str.split(' ')[1])
    
    pc_list = list(set(pc_list_raw))
	
    for i in pc_list:
        if (i == 'None'):
            pc_list.remove(i)
	
	#pc_list.remove('None')

    if(len(pc_list) != 0):
        pc_list_str=','.join(pc_list)
        output.append('%s,%s' %(pc,pc_list_str))
		
	
with open(outfile,'w') as f:
    for i in output:
        f.write('%s\n' % i)



