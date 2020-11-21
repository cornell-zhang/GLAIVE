#!/usr/bin/python

# This script calculates store equivalence classes.

import os
import random
import sys

from equiv_class import equiv_class
from inst_database import instruction
from register import x86_register
from trace import trace_item

class basic_block(object):
    def __init__(self,bb_id):
        self.bb_id = bb_id
        self.insts = []
        self.st_insts = []
        self.st_inst_idx = []
        self.size = 0

    def __repr__(self):
        return 'basic block: %s' % (self.bb_id)

class static_st_inst(object):
    def __init__(self,pc):
        self.pc = pc
        self.dynamic_pcs = {}

        self.equiv_classes = {}

    def __repr__(self):
        return 'store store info at pc %s' % (self.pc)

    def add_inst_num(self,inst_num,addr):
        '''
        adds a dynamic PC to the static instruction.
        Args: inst_num - instruction number (in ticks)
              addr - target address of store
        '''
        self.dynamic_pcs[inst_num] = st_inst(self.pc, inst_num, addr)

    def create_equiv_class(self):
        '''
        creates the equivalence classes once all loads and stores have been
        recorded successfully.
        '''
        for inst_num in self.dynamic_pcs:
            dynamic_pc = self.dynamic_pcs[inst_num]
            # loads can be used as a key to quickly lookup if the pattern
            # has been seen before
            load_pattern = ','.join(dynamic_pc.loads)
            if load_pattern not in self.equiv_classes:
                self.equiv_classes[load_pattern] = equiv_class(self.pc)
            self.equiv_classes[load_pattern].add_member(inst_num)
            
    def print_equiv_classes(self):
        '''
        outputs all equivalence classes for this static PC.
        Returns: output - information fo equivalence class
        '''
        output = ''
        for equiv_class in self.equiv_classes:
            self.equiv_classes[equiv_class].select_pilot()
            output += '%s\n' % \
                       self.equiv_classes[equiv_class].print_equiv_class()
        return output

class st_inst(object):
    def __init__(self,pc,inst_num,addr):
        self.pc = pc
        self.inst_num = inst_num
        self.addr = addr
        self.loads = []

    def __repr__(self):
        return 'dynamic store pc: %s addr: %s inst_num: %s' % \
                (self.pc, self.addr, self.inst_num)
        
    def add_load(self,load_pc):
        self.loads.append(load_pc)

    

class depending_instructions(object):
    def __init__(self):
        '''
        initializes a map of instructions where the key is the static PC,
        and the value is the PC of the store that depends on it
        '''
        self.dep_inst_map = {}

    def add_dep_inst(self,dep_inst_pc,st_inst_pc):
        '''
        updates the dependent store instruction
        Args: dep_inst_pc - PC of instruction that store depends on
              st_inst_pc - PC of dependent store
        '''
        if dep_inst_pc not in self.dep_inst_map:
            self.dep_inst_map[dep_inst_pc] = None
        self.dep_inst_map[dep_inst_pc] = st_inst_pc

    def print_dep_insts(self):
        '''
        prints out the depending instructions for the appropriate stores
        Returns: output - string format for each instruction
        '''
        output = ''
        dep_pcs = sorted(self.dep_inst_map.keys())
        output += 'dep_pc store_pc\n'
        for dep_pc in dep_pcs:
            output += '%s %s\n' % (dep_pc, self.dep_inst_map[dep_pc])
        return output
        
        

class store_equivalence(object):
    def __init__(self, app_name, app_prefix):
        self.app_name = app_name

        inst_db_file = app_prefix + '_parsed.txt'
        
        # get instruction database of application
        inst_db = open(inst_db_file).read().splitlines()
        
        # first field is ignored since it contains only headers
        self.insts = [instruction(None,None,i) for i in inst_db[1:]]
        
        self.insts_map = {inst.pc:inst for inst in self.insts}
        
        # get trace data to build basic blocks and store equiv classes
        # self.exec_trace = trace(mem_filename) 
        self.trace_filename = app_prefix + '_clean_dump_parsed_merged.txt'

        # used to check alias of register when creating dependency chains
        self.x86_regs = x86_register()

        self.basic_blocks_map = {}
        self.st_inst_pcs = set()
        self.ld_inst_pcs = set()

        self.dep_insts = depending_instructions()

        self.static_st_inst_map = {}
        self.addr_map = {}  # holds info on latest store accessing an address

    def _add_ld_or_st_pc(self, item, curr_bb):
        '''
        TODO: fill signature
        '''
        pc = item.pc
        if item.mem_op is not None:
            if item.mem_op == 'Read':
                self.ld_inst_pcs.add(pc)
            elif item.mem_op == 'Write':
                self.st_inst_pcs.add(pc)
                curr_bb.st_insts.append(self.insts_map[pc])
                curr_bb.st_inst_idx.append(curr_bb.size)
        

    def build_basic_blocks(self):
        '''
        uses the execution trace to build basic blocks. The basic blocks
        are used to find the instructions that each store instruction
        depends on.
        '''
        with open(self.trace_filename) as exec_trace:
            curr_bb = None
            create_new_bb = False 
            # iterate through the trace, create store chains and bbs in the process
            start_processed = False
            for line in exec_trace:
                items = line.split()
                item = trace_item(items)
                pc = item.pc
                # very first instruction executed, start of bb
                if not start_processed:
                    curr_bb = basic_block(pc)
                    start_processed = True
                    
                # check if pc is control inst, end bb
                if self.insts_map[pc].ctrl_flag: 
                    if not create_new_bb:
                        if curr_bb.bb_id not in self.basic_blocks_map:
                            self.basic_blocks_map[curr_bb.bb_id] = curr_bb
                        create_new_bb = True
                if create_new_bb:
                    # first inst of bb should not be control
                    if not self.insts_map[pc].ctrl_flag:
                        start = pc
                        curr_bb = basic_block(start)
                        create_new_bb = False
                        curr_bb.insts.append(self.insts_map[pc])
                        self._add_ld_or_st_pc(item, curr_bb)
                        curr_bb.size += 1
                else:
                    curr_bb.insts.append(self.insts_map[pc])
                    self._add_ld_or_st_pc(item, curr_bb)
                    curr_bb.size += 1
            # make a final basic block after iterating
            if curr_bb.bb_id not in self.basic_blocks_map:
                self.basic_blocks_map[curr_bb.bb_id] = curr_bb

    def _add_src_regs(self, pc):
        '''
        adds to the list of currently active source registers when computing
        store dependence chains.
        Args: pc - PC of the current instruction to get registers from
        Returns: list of registers that belong to the requested instruction
        '''
        temp_regs = self.insts_map[pc].src_regs+self.insts_map[pc].mem_src_regs
        while None in temp_regs:
            temp_regs.remove(None)
        return temp_regs

    def find_depending_instructions(self):
        '''
        finds the depending instructions of every store, given the basic blocks
        of an application.
        '''
        for bb_id in self.basic_blocks_map:
            bb = self.basic_blocks_map[bb_id]
            # iterate through stores and bb in reverse
            for i in range(len(bb.st_insts)-1,-1,-1):
                curr_regs = []
                curr_st = bb.st_insts[i]
                curr_st_idx = bb.st_inst_idx[i]
                pc = curr_st.pc
                curr_regs += self._add_src_regs(pc)
                inst_idx = curr_st_idx - 1
                # make sure that we stop at the basic block
                # or when all regs are used
                while inst_idx > 0 and len(curr_regs) > 0:
                    curr_inst = bb.insts[inst_idx]
                    pc = curr_inst.pc
                    if pc not in self.st_inst_pcs:
                        dest_reg = curr_inst.dest_reg
                        if dest_reg is not None:
                            for reg in curr_regs:
                                # we found a def of one of the registers
                                if self.x86_regs.is_alias(dest_reg, reg):
                                    curr_regs.remove(reg)
                                    curr_regs += self._add_src_regs(pc)
                                    self.dep_insts.add_dep_inst(pc, curr_st.pc)
                                    break
                    inst_idx -= 1

    def print_depending_instructions(self,out_filename):
        '''
        prints out the depending instructions.
        Args: out_filename - name of file to output
        '''
        output = open(out_filename, 'w')
        output_lines = self.dep_insts.print_dep_insts()
        output.write(output_lines)
        output.close()

    def create_store_equiv_classes(self):
        '''
        creates store equivalence classes by tracking loads and stores
        as well as their addresses.
        '''
        # simplify trace so that only loads and stores are checked
        simple_trace = []
        with open(self.trace_filename) as exec_trace:
            for line in exec_trace:
                items = line.split()
                item = trace_item(items)
                if item.mem_op is not None:
                    simple_trace.append(item)                

        for item in simple_trace:
            inst_num = item.inst_num
            pc = item.pc
            mem_op = item.mem_op
            addr = item.mem_addr
            if mem_op == 'Read':
                if addr in self.addr_map:
                    # there exists a store that the load is reading from
                    self.addr_map[addr].add_load(pc)
            elif mem_op == 'Write' and not self.insts_map[pc].ctrl_flag:
                if pc not in self.static_st_inst_map:
                    self.static_st_inst_map[pc] = static_st_inst(pc)
                self.static_st_inst_map[pc].add_inst_num(inst_num,addr)
                dynamic_pc = self.static_st_inst_map[pc].dynamic_pcs[inst_num]
                # record the address of the store to check subsequent loads
                self.addr_map[addr] = dynamic_pc
        for static_pc in self.static_st_inst_map:
            self.static_st_inst_map[static_pc].create_equiv_class()
                
    def print_store_equiv_classes(self, out_filename):
        '''
        prints the store equivalence classes to a file.
        Args: out_filename - name of file to output
        '''
        outfile = open(out_filename, 'w')
        output = 'pc:population:pilot:members\n'
        for pc in self.static_st_inst_map:
            output += self.static_st_inst_map[pc].print_equiv_classes()
        outfile.write(output)
        outfile.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python store_equivalence.py [app_name] [isa]')
        exit()

    app_name = sys.argv[1]
    isa = sys.argv[2]

    approx_dir = os.environ.get('APPROXGEM5')
    apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    app_prefix = apps_dir + '/' + app_name

    store_equiv = store_equivalence(app_name, app_prefix)
    store_equiv.build_basic_blocks()
    store_equiv.find_depending_instructions()
    
    out_filename = app_prefix + '_dependent_stores.txt'
    store_equiv.print_depending_instructions(out_filename)
    
    out_filename = app_prefix + '_store_equivalence.txt'
    store_equiv.create_store_equiv_classes()
    store_equiv.print_store_equiv_classes(out_filename)
