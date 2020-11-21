#!/usr/bin/python

# This script generates def-use pairs.

import os
import sys

from inst_database import inst_database
from inst_database import instruction
from register import x86_register
from register import x86_def_register

class x86_reg_collection(object):
    def __init__(self):
        reg_set = x86_register()
        self.x86_reg_map = {}
        self.x86_full_regs = set()
        for reg in reg_set.reg_alias_map:
            self.x86_full_regs.add(reg_set.reg_alias_map[reg])
        for full_reg in self.x86_full_regs:
            self.x86_reg_map[full_reg] = x86_def_register(full_reg, None)

    def clear_regs(self):
        for reg in self.x86_reg_map:
            self.x86_reg_map[reg].update_def(reg, None)

    def __getitem__(self, reg_name):
        return self.x86_reg_map[reg_name]
            


class def_use_pc_database(object):
    def __init__(self,app_name,inst_db_filename,create_inst_db=False):
        
        insts = []
        if create_inst_db:
            dis_filename = inst_db_filename
            inst_db = inst_database(dis_filename)
            insts = inst_database.insts
        else:
            db_file = inst_db_filename
            # read and organize disassembly info (1st line is just header)
            db_info = [i for i in open(db_file).read().splitlines()[1:]]
            insts = [instruction(None,None,i) for i in db_info]

        pc_list = [inst.pc for inst in insts]
        pc_def_map = {}

        x86_regs = x86_register()

        x86_active_regs = x86_reg_collection() 

        for inst in insts:
            pc = inst.pc
            is_ctrl_op = inst.ctrl_flag
            src_regs = inst.src_regs + inst.mem_src_regs
            dest_reg = inst.dest_reg
            if is_ctrl_op:  # reset map once leaving basic block
                x86_active_regs.clear_regs()
            else:
                for i in range(len(src_regs)):
                    src_reg = src_regs[i]
                    alias_reg = x86_regs.reg_alias_map[src_reg]
                    alias_dest_reg = x86_active_regs[alias_reg]
                    src_reg_size = x86_regs.reg_size_map[src_reg]
                    # check for registers such as 'ah'
                    if src_reg_size == -1:
                        bit_range_pc = alias_dest_reg.bit_ranges[1]
                        if bit_range_pc is not None:
                            pc_def_map[bit_range_pc].update_first_use(1, pc)
                    else:
                        for j in range(src_reg_size):
                            bit_range_pc = alias_dest_reg.bit_ranges[j]
                            if bit_range_pc is not None:
                                pc_def_map[bit_range_pc].update_first_use(j, pc)
                if dest_reg is not None:
                    pc_def_map[pc]=x86_def_register(dest_reg, pc)
                    alias_reg = x86_regs.reg_alias_map[dest_reg]
                    x86_active_regs[alias_reg].update_def(dest_reg, pc)

        self.pc_list = pc_list
        self.pc_def_map = pc_def_map

    def print_db(self,output_filename):
        '''
        prints the def_use database. 
        Args: output_filename - desired filename for database
        '''
        output = open(output_filename, 'w')
        output.write('pc reg 0-8 8-16 16-32 32-64\n')
        for pc in self.pc_list:
            if pc in self.pc_def_map:
                output.write('%s\n' % self.pc_def_map[pc])
        output.close()

    def __getitem__(self, pc):
        return self.pc_def_map[pc]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python def_use.py [app_name] [isa]')
        exit()

    app_name = sys.argv[1]
    isa = sys.argv[2]

    approx_dir = os.environ.get('APPROXGEM5')
    apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    app_prefix = apps_dir + '/' + app_name

    inst_db_filename = app_prefix + '_parsed.txt'
    def_use_db = def_use_pc_database(app_name,inst_db_filename)
    output_file = app_prefix + '_def_use.txt'
    def_use_db.print_db(output_file)

