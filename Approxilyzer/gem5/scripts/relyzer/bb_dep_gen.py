#!/usr/bin/python
#jiajia jiao

import os
import sys

from inst_database import instruction
from trace import trace_item

if len(sys.argv)!= 3:
	print ('Usage: python bb_dep_gen.py [app_name] [isa]')
	exit()
app_name=sys.argv[1]
isa = sys.argv[2]


approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name
db_filename = app_prefix + '_parsed.txt'
trace_filename = app_prefix + '_clean_dump_parsed_merged.txt'

# add thes part to print the control flow graph
cfg_node_filename = app_prefix + '_cfg_node.txt'
cfg_edge_filename = app_prefix + '_cfg_edge.txt'


db_info = [i for i in open(db_filename).read().splitlines()[1:]]
insts = [instruction(None,None,i) for i in db_info]
ctrl_insts = set([i.pc for i in insts if i.ctrl_flag])


# list of basic blocks. Each list element is a 2-length list with
# first element as start PC and second as end PC
basicblocks = set() # defaultdict(int)

# program represented as basic blocks with tick value at start of basic block
program_bb = [] 

with open(trace_filename) as trace:
    start_of_bb = True
    pc = None

    for line in trace:
        items = line.split()
        item = trace_item(items)
        pc = item.pc
        inst_num = item.inst_num
        if pc in ctrl_insts:
            if not start_of_bb:
                start_of_bb = True
        elif start_of_bb:
            basicblocks.add(pc)
            program_bb.append([inst_num, pc])
            start_of_bb = False


bb_list = []
program_bb_list = []

# insert the spart to get all PCs for each block
with open (trace_filename) as trace:
	#pc_list = None
	start_of_bb = False
	for line in trace:
		items = line. split()
		item = trace_item(items)
		pc = item.pc
		if pc in basicblocks:
			bb_list.append(pc)
			if not start_of_bb:
				#print('start----%s \n' % pc)
				start_of_bb = True
				#bb_list.append(pc)
		elif start_of_bb:
			bb_list.append(pc)
			if pc in ctrl_insts:
				star_of_bb = False
				#pc_list = ''.join(bb_list)
				if bb_list not in program_bb_list and len(bb_list) > 1:
				#if bb_list not in program_bb_list :
					program_bb_list.append(bb_list)
				bb_list = []
		
#print ('number of pgram bb list : ', len(program_bb_list))
	
with open(cfg_node_filename,'w') as f:
	for bb in program_bb_list:
		for pc in bb:
			f.write('%s , ' % pc )
		f.write('\n')
	
with open(cfg_edge_filename,'w') as f:
	for bb in basicblocks:
		f.write ('%s \n' % bb)


