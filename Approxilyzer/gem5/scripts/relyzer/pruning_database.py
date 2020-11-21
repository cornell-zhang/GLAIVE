#!/usr/bin/python

# This script combines analysis files (control, store, def-use, addr)
# in order to create a pruning database.

import os
import shutil
import sys

from equiv_class import equiv_class
from inst_database import instruction
from trace import trace_item

# object to collect static pc info in fault database
class pc_info(object):
    def __init__(self, pc, max_bits, pilot=None, is_mem=False, 
                 in_string=None):
        if in_string is None:
            self.pc = pc
            self.ctrl_or_store = None
            self.def_pc = None
            self.do_inject = True
            self.src_regs = None
            self.mem_src_regs = None
            self.dest_reg = None
            self.is_mem = is_mem
            self.pilot = pilot
            self.max_bits = max_bits
        else:
            temp = in_string.split()
            self.pc = temp[0]
            self.ctrl_or_store = temp[1]
            self.def_pc = None if temp[2] == 'None' else simple_def_reg(
                          None,None,in_string=temp[2])
            self.do_inject = True if temp[3] == 'True' else False
            self.src_regs = None if temp[4] == 'None' else temp[4].split(',') 
            self.mem_src_regs = None if temp[5] == 'None' else \
                                temp[5].split(',')
            self.dest_reg = None if temp[6] == 'None' else temp[6]
            self.is_mem = True if temp[7] == 'True' else False
            self.pilot = temp[8]
            self.max_bits = int(temp[9])
    def __repr__(self):
        return 'PC object:%s' % self.pc

class simple_def_reg(object):
    def __init__(self, reg, bit_width, in_string=None):
        if in_string is None:
            self.reg = reg
            self.bit_width = bit_width
        else:
            temp = in_string.split(':')
            self.reg = temp[0]
            self.bit_width = temp[1:]
    def __repr__(self):
        return '%s:%s' % (self.reg,':'.join(self.bit_width))

def check_string(obj):
    string = 'None'
    if obj is not None:
        if len(obj) > 0:
            string = obj
    return string

class pruning_database(object):
    def __init__(self, app_name, apps_dir):

        self.app_name = app_name
        ignored_ops = {'prefetch'}

        app_prefix = apps_dir + '/' + app_name
        trace_file = app_prefix + '_clean_dump_parsed_merged.txt'
        ctrl_equiv_file = app_prefix + '_control_equivalence.txt'
        store_equiv_file = app_prefix + '_store_equivalence.txt'
        dep_stores_file = app_prefix + '_dependent_stores.txt'
        def_use_file = app_prefix + '_def_use.txt'
        db_file = app_prefix + '_parsed.txt'


        ctrl_equiv_info = [i.split(':')[0:3] for i in open(
                ctrl_equiv_file).read().splitlines()[1:]]
        store_equiv_info = [i.split(':')[0:3] for i in open(
                store_equiv_file).read().splitlines()[1:]]
        self.def_use_info = {i.split()[0]:simple_def_reg(
                        i.split()[1],i.split()[2:6]) for i in open(
                        def_use_file).read().splitlines()[1:]}
        
        store_equiv_pilots = set([i[2] for i in store_equiv_info])

        dep_stores_list = open(dep_stores_file).read().splitlines()[1:]
        dep_stores_info = {}

        for item in dep_stores_list:
            temp = item.split()
            dep_pc = temp[0]
            store_pc = temp[1]
            if store_pc not in dep_stores_info:
                dep_stores_info[store_pc] = []
            dep_stores_info[store_pc].append(dep_pc) 

        store_equiv_pcs = set()

        db_info = [i for i in open(db_file).read().splitlines()[1:]]
        insts = [instruction(None,None,i) for i in db_info]
        self.inst_db_map = {i.pc:i for i in insts}
        self.ctrl_insts = set([i.pc for i in insts if i.ctrl_flag])

        # trace_info = trace(trace_file)

        self.pc_map = {}


        pc_idx = 0
        pilot_idx = 2
        member_idx = 3 

        # new_store_equiv_file = app_prefix + '_final_store_equivalence.txt'
        # new_ctrl_equiv_file = app_prefix + '_final_control_equivalence.txt'

        dep_stores_equiv_classes = []

        dep_stores_pilot_map = {}
        for item in store_equiv_info:
            pc = item[pc_idx]
            pilot = item[pilot_idx]
            # members = item[member_idx].split()
            self._add_to_pc_map(pc, pilot, 'store')
            store_equiv_pcs.add(pc)

        with open(trace_file) as f:
            curr_bb = {}
            for line in f:
                item = trace_item(line.split())
                if item.pc in self.ctrl_insts:
                    curr_bb = {}
                curr_bb[item.pc] = item.inst_num
                # store that depends on prev insts
                if item.inst_num in store_equiv_pilots and item.pc in dep_stores_info:
                    for dep_pc in dep_stores_info[item.pc]:
                        if dep_pc in curr_bb:
                            self._add_to_pc_map(
                                    dep_pc,
                                    curr_bb[dep_pc], 'store')
                            store_equiv_pcs.add(dep_pc)

            # build non-store pc equivalence classes for
            # store equivalence (previously in control_equiv file)
            # if pc in dep_stores_info:
            #     for dep_pc in dep_stores_info[pc]:
            #         dep_pc_pilot = ''
            #         dep_pc_equiv = equiv_class(dep_pc)
            #         is_ctrl = False
            #         for member in members:
            #             store_idx = trace_info.get_idx(member)
            #             added_to_pc_map = False
            #             for i in range(store_idx,-1,-1):
            #                 trace_item = trace_info[i]
            #                 is_ctrl = self.inst_db_map[
            #                         trace_item.pc].ctrl_flag
            #                 if is_ctrl:
            #                     if dep_pc in store_equiv_pcs:
            #                         store_equiv_pcs.remove(dep_pc)
            #                     if added_to_pc_map:
            #                         self._remove_from_pc_map(dep_pc)
            #                     dep_stores_info[pc].remove(dep_pc)
            #                     break
            #                 if trace_item.pc == dep_pc:
            #                     if member == pilot:
            #                         dep_pc_pilot = trace_item.inst_num
            #                         self._add_to_pc_map(dep_pc,dep_pc_pilot,
            #                                             'store')
            #                         added_to_pc_map = True
            #                         store_equiv_pcs.add(dep_pc)
            #                     dep_pc_equiv.add_member(
            #                             trace_item.inst_num) 
            #                     break
            #             if is_ctrl:
            #                 break
            #         dep_pc_equiv.set_pilot(dep_pc_pilot)
            #         if not is_ctrl:
            #             dep_stores_equiv_classes.append(dep_pc_equiv)

        # new_ctrl_info = []  # stores pcs that stores do not depend on 
        for item in ctrl_equiv_info:
            pc = item[pc_idx]
            pilot = item[pilot_idx]
            if pc not in store_equiv_pcs:
                self._add_to_pc_map(pc, pilot, 'ctrl') 
                # new_ctrl_info.append(item)

        # update final equivalence class files
        # with open(new_ctrl_equiv_file, 'w') as f:
        #     for item in new_ctrl_info:
        #         f.write('%s\n' % ':'.join(item))

        # del new_ctrl_info
        # 
        # shutil.copy(store_equiv_file,new_store_equiv_file)    
        # with open(new_store_equiv_file, 'a') as f:
        #     for item in dep_stores_equiv_classes: 
        #         f.write('%s\n' % item.print_equiv_class())            

        # del dep_stores_equiv_classes
        
        self.pc_list = sorted(self.pc_map.keys())
            
   
            
    def _add_to_pc_map(self, pc, pilot, ctrl_or_store):
        inst_info = self.inst_db_map[pc]
        pc_obj = pc_info(pc,inst_info.max_bits,pilot=pilot,
                         is_mem=inst_info.is_mem)
        pc_obj.ctrl_or_store = ctrl_or_store
        pc_obj.src_regs = inst_info.src_regs
        pc_obj.mem_src_regs = inst_info.mem_src_regs
        pc_obj.dest_reg = inst_info.dest_reg
        pc_obj.def_pc = self.def_use_info.get(pc, 'None')
        if len(pc_obj.src_regs) == 0 and len(pc_obj.mem_src_regs) == 0 \
                and pc_obj.dest_reg is None:
            pc_obj.do_inject = False

        
        if pc not in self.pc_map:
            self.pc_map[pc] = []
        self.pc_map[pc].append(pc_obj)
    
    def _remove_from_pc_map(self, pc):
        curr_pc_obj = self.pc_map[pc][-1]  # get last element added to list
        if curr_pc_obj.ctrl_or_store == 'store':
            self.pc_map[pc].pop()

    def print_pruning_db(self,filename):
        
        output_file = filename
        output = open(output_file, 'w')
        output.write('pc ctrl_or_store def_pc do_inject src_regs mem_src_regs dest_reg is_mem pilot max_bits\n')
        for pc in self.pc_list:
            for pc_obj in self.pc_map[pc]:
                def_pc = pc_obj.def_pc
                ctrl_or_store = pc_obj.ctrl_or_store
                do_inject = pc_obj.do_inject
                src_regs = check_string(','.join(pc_obj.src_regs))
                mem_src_regs = check_string(','.join(pc_obj.mem_src_regs))
                dest_reg = check_string(pc_obj.dest_reg)
                is_mem = pc_obj.is_mem
                pilot = check_string(pc_obj.pilot)
                max_bits = pc_obj.max_bits
                output.write('%s %s %s %r %s %s %s %r %s %d\n' % (
                    pc, ctrl_or_store, def_pc,
                    do_inject, src_regs, mem_src_regs, dest_reg,
                    is_mem, pilot, max_bits))
        output.close()
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python gen_pruning_database.py [app_name] [isa]')
        exit()

    app_name = sys.argv[1]
    isa = sys.argv[2]

    approx_dir = os.environ.get('APPROXGEM5')

    apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name

    pruning_db = pruning_database(app_name, apps_dir)
    pruning_db.print_pruning_db(
        apps_dir + '/' + app_name + '_pruning_database.txt') 
