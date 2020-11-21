#!/usr/bin/python

# processes the raw injections by adding in information from the pruning
# database

import os
import sys

from equiv_class import equiv_class_database
from pruning_database import pc_info
from inj_create import x86_inj_functions
from trace import trace

if len(sys.argv) != 3:
    print('Usage: python postprocess.py [app_name] [isa]')
    exit()

app_name = sys.argv[1]
isa = sys.argv[2]

approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name

raw_outcomes_path = approx_dir + '/gem5/outputs/x86/'

raw_trace_file = app_prefix + '_clean_dump_parsed_merged.txt'
pruning_db_file = app_prefix + '_pruning_database.txt'
raw_outcomes_file = raw_outcomes_path + app_name + '.outcomes_raw'
mem_bounds_file = app_prefix + '_mem_bounds.txt'

dependent_stores_file = app_prefix + '_dependent_stores.txt'


app_trace = trace(raw_trace_file)

mem_bounds = [int(i) for i in open(mem_bounds_file).read().splitlines()[1].split()]
mem_bit_start = max(mem_bounds)

raw_outcomes_list = open(raw_outcomes_file).read().splitlines()

pruning_db = [pc_info(None,None,None,in_string=i) for i in open(
              pruning_db_file).read().splitlines()[1:]]

pilot_db_map = {i.pilot:i for i in pruning_db}

ctrl_equiv_db = equiv_class_database(app_prefix + '_final_control_equivalence.txt')
store_equiv_db = equiv_class_database(app_prefix + '_final_store_equivalence.txt')
x86_inj = x86_inj_functions()

dependent_stores_info = {i.split()[0]:i.split()[1] for i in open(
        dependent_stores_file).read().splitlines()[1:]}

pilot_reg_bit_outcomes = {}

output = []
for item in raw_outcomes_list:
    inj = item.split('::')[0]  # get injection info
    outcome = item.split('::')[1]
    temp = inj.split(',')
    pilot = temp[1]
    reg = temp[2]
    bit = temp[3] 
    pilot_reg_bit_outcomes[(pilot,reg,bit)] = (inj,outcome)
    pc = pilot_db_map[pilot].pc
    ctrl_or_store = pilot_db_map[pilot].ctrl_or_store
    if ctrl_or_store == 'store':
        # for non-store instructions
        if pc in dependent_stores_info:
            curr_pilot_idx = app_trace.get_idx(pilot)
            store_pc = dependent_stores_info[pc]
            i = curr_pilot_idx
            for i in range(curr_pilot_idx,len(app_trace)):
                if app_trace[i].pc == store_pc:
                    ctrl_or_store += ',%s,%s' % (
                            store_pc, app_trace[i].inst_num)
                    break
            else:
                print('Error: no store found, check trace')
                exit()
            
            
    output.append('%s,%s::%s::inj' % (pc, item, ctrl_or_store))

for pilot in pilot_db_map:
    pc_obj = pilot_db_map[pilot]
    if pc_obj.is_mem and pc_obj.do_inject and pc_obj.mem_src_regs is not None:
        for reg in pc_obj.mem_src_regs:
            injs = x86_inj.create_inj('x86', pilot, reg, 
                                    pc_obj.max_bits, mem_bit_start)
            for inj in injs:
                output.append('%s,%s::Detected::%s::pruned:mem_bounds' % (
                      pc_obj.pc,inj,pc_obj.ctrl_or_store))
    if pc_obj.def_pc is not None:
        use_pc_map = {}
        injs,use_pcs = x86_inj.create_pruned_def_inj('x86', pilot, \
                       pc_obj.pc, pc_obj.def_pc, pc_obj.max_bits)
        for i,use_pc in enumerate(use_pcs):
            # optimization: store corresponding inst_num 
            if use_pc not in use_pc_map:
                curr_pilot_idx = app_trace.get_idx(pilot) 
                trace_item = app_trace[curr_pilot_idx] 
                while trace_item.pc != use_pc:
                    curr_pilot_idx += 1
                    trace_item = app_trace[curr_pilot_idx]
                # get inst_num of first_use
                use_pc_map[use_pc] = trace_item.inst_num
            temp = injs[i].split(',')
            reg = temp[2]
            bit = temp[3] 
            use_pilot = ctrl_equiv_db.get_pilot(use_pc_map[use_pc])
            if use_pilot is None:
                use_pilot = store_equiv_db.get_pilot(use_pc_map[use_pc])
            if (use_pilot,reg,bit) not in pilot_reg_bit_outcomes:
                output.append('%s,%s::Detected::%s::pruned:mem_bounds' % (
                      pc_obj.pc,injs[i],pc_obj.ctrl_or_store))
            else:
                use_inj,outcome = pilot_reg_bit_outcomes[(use_pilot,reg,bit)]
                output.append('%s,%s::%s::%s::pruned:%s,%s' % (
                        pc_obj.pc,injs[i],outcome,pc_obj.ctrl_or_store,
                        use_pc,use_inj))
outfile = app_prefix + '_postprocess.txt'
with open(outfile,'w') as f:
    for i in output:
        f.write('%s\n' % i)
