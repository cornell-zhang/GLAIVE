#!/usr/bin/python

# This script uses the pruning database with the register info 
# and outputs final injection list.

import os
import sys
import random

from equiv_class import equiv_class_database
from pruning_database import pc_info
from trace import trace



int_reg_info_64 = [ 'rax', 'rbx', 'rcx', 'rdx', 'rbp', 'rsi', 'rdi',
                'rsp', 'rip', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13',
                'r14', 'r15' ]

int_reg_info_32 = [ 'eax', 'ebx', 'ecx', 'edx', 'ebp', 'esi', 'edi',
                'esp', 'eip' ]
int_reg_info_16 = [ 'ax', 'bx', 'cx', 'dx', 'bp', 'si', 'di', 'sp', 'ip' ]

int_reg_info_8 = [ 'ah', 'bh', 'ch', 'dh', 'al', 'bl', 'cl', 'dl' ] 

upper_regs = set([ 'ah', 'bh', 'ch', 'dh' ])

float_reg_info_128 = [ 'xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4' , 'xmm5',
                       'xmm6', 'xmm7', 'xmm8', 'xmm9', 'xmm10', 'xmm11',
                       'xmm12', 'xmm13', 'xmm14', 'xmm15' ]

float_reg_info_64 = [ 'fpr0', 'fpr1', 'fpr2', 'fpr3', 'fpr4',
        'fpr5', 'fpr6', 'fpr7' ]

# set corresponding register info into map data structures
reg_bits_map = {}
reg_int_float_map = {}

for i in int_reg_info_64:
    reg_bits_map[i] = 64
    reg_int_float_map[i] = 0

for i in int_reg_info_32:
    reg_bits_map[i] = 32
    reg_int_float_map[i] = 0

for i in int_reg_info_16:
    reg_bits_map[i] = 16
    reg_int_float_map[i] = 0

for i in int_reg_info_8:
    reg_bits_map[i] = 8
    reg_int_float_map[i] = 0

for i in float_reg_info_128:
    reg_bits_map[i] = 64 # TODO: need to account for SIMD in the future
    reg_int_float_map[i] = 1

for i in float_reg_info_64:
    reg_bits_map[i] = 64
    reg_int_float_map[i] = 1

def_use_count_map = {}
addr_bound_count_map = {}
pc_pilot_map = {}

ctrl_equiv_inj = 0
store_equiv_inj = 0

# TODO: cleanup within script, used externally for postprocessing
class x86_inj_functions(object):
    def _print_inj(self, isa, pilot, bit_pos, reg, reg_type, src_dest):
        return '%s,%s,%s,%s,%s,%s' % (isa, pilot, reg, bit_pos,
                    reg_type, src_dest)

    def _print_def_inj(self, isa, pilot, bit_start, bit_stop, \
                       reg, reg_type, injs, use_pc, use_pcs):
        for bit in range(bit_start, bit_stop):
            injs.append(self._print_inj(
                    isa, pilot, bit, reg, reg_type, 1))
            use_pcs.append(use_pc)
        

    def create_inj(self, isa, pilot, reg, max_bits, bit_start):
        '''
        used for source registers only (0 passed in to src_dest)
        '''
        reg_max_bits = reg_bits_map[reg]
        reg_type = reg_int_float_map[reg]
        max_iters = min(reg_max_bits, max_bits)
        injs = []
        for bit in range(bit_start, max_iters):
            injs.append(self._print_inj(isa, pilot, bit, reg, reg_type, 0))
        return injs

    def create_pruned_def_inj(self, isa, pilot, pc, def_pc, max_bits):
        reg = def_pc.reg
        reg_max_bits = reg_bits_map[reg]
        reg_type = reg_int_float_map[reg]
        bit_width = def_pc.bit_width

        injs = []
        use_pcs = []
        # edge case where only bits [15:8] are checked (like %ah)
        if reg in upper_regs:
            if bit_width[1] != pc and bit_width[1] != 'None':
                self._print_def_inj(isa, pilot, 0, reg_max_bits, reg, \
                                    reg_type, injs, bit_width[1], use_pcs)
        else:
    # go through the bit widths and only print if there was a use
            if bit_width[0] != pc and bit_width[0] != 'None':
                self._print_def_inj(isa, pilot, 0, 8, reg, \
                                    reg_type, injs, bit_width[0], use_pcs)
            if bit_width[1] != pc and bit_width[1] != 'None':
                self._print_def_inj(isa, pilot, 8, 16, reg, \
                                    reg_type, injs, bit_width[1], use_pcs)
            if bit_width[2] != pc and bit_width[2] != 'None':
                self._print_def_inj(isa, pilot, 16, 32, reg, \
                                    reg_type, injs, bit_width[2], use_pcs)
            if bit_width[3] != pc and bit_width[3] != 'None':
                self._print_def_inj(isa, pilot, 32, min(64,max_bits), reg, \
                                    reg_type, injs, bit_width[3], use_pcs)
        return injs,use_pcs

def print_inj(isa, pilot, bit_pos, reg, reg_type, src_dest):
    return '%s,%s,%s,%s,%s,%s' % (isa, pilot, reg, bit_pos,
                reg_type, src_dest)

def create_inj(pc, isa, pilot, reg, max_bits, mem_bound=64):
    '''
    used for source registers only (0 passed in to src_dest)
    '''
    global addr_bound_count_map

    reg_max_bits = reg_bits_map[reg]
    reg_type = reg_int_float_map[reg]
    max_iter_bits = min(reg_max_bits, max_bits, mem_bound)
    if pc not in addr_bound_count_map:
        addr_bound_count_map[pc] = {}
    if pilot not in addr_bound_count_map[pc]:
        addr_bound_count_map[pc][pilot] = 0
    if mem_bound < reg_max_bits and mem_bound < max_bits:
        addr_bound_count_map[pc][pilot] += min(reg_max_bits,max_bits) - mem_bound
        

    injs = []

    for bit in range(max_iter_bits):
        injs.append(print_inj(isa, pilot, bit, reg, reg_type, 0))
    return injs

def create_def_inj(isa, pilot, pc, def_pc, max_bits):
    reg = def_pc.reg
    reg_max_bits = reg_bits_map[reg]
    reg_type = reg_int_float_map[reg]
    bit_width = def_pc.bit_width

    global def_use_count_map
    def_use_count = 0
    injs = []
    # edge case where only bits [15:8] are checked (like %ah)
    if reg in upper_regs:
        if bit_width[1] == pc:
            for bit in range(reg_max_bits):
                injs.append(print_inj(isa, pilot, bit, reg, reg_type, 1))
        elif bit_width[1] != 'None':
            def_use_count += 8
    else:
        # go through the bit widths and only inject if there was no first use
        if bit_width[0] == pc:
            for bit in range(8):
                injs.append(print_inj(isa, pilot, bit, reg, reg_type, 1))
        elif bit_width[0] != 'None':
            def_use_count += 8
        if bit_width[1] == pc:
            for bit in range(8,16):
                injs.append(print_inj(isa, pilot, bit, reg, reg_type, 1))
        elif bit_width[1] != 'None':
            def_use_count += 8
        if bit_width[2] == pc:
            for bit in range(16,32):
                injs.append(print_inj(isa, pilot, bit, reg, reg_type, 1))
        elif bit_width[2] != 'None':
            def_use_count += 16
        if bit_width[3] == pc:
            for bit in range(32,min(max_bits,64)):
                injs.append(print_inj(isa, pilot, bit, reg, reg_type, 1))
        elif bit_width[3] != 'None':
            if max_bits > 32:
                def_use_count += 32
    def_use_count_map[pc] = def_use_count
    return injs

def add_regs(regs_list, regs):
    if regs is not None:
        if isinstance(regs,(list,)):
            regs_list += regs
        else:  # dest reg is currently just a string
            regs_list.append(regs)

def collect_stats(app_name, app_prefix, pruning_db, total_inj):
    global def_use_count_map
    global addr_bound_count_map
    global pc_pilot_map
    global ctrl_equiv_inj
    global store_equiv_inj
    total_err_sites = 0
    def_use_total = 0
    addr_bound_total = 0
    store_equiv_total = 0
    ctrl_equiv_total = 0

    store_equiv_db = equiv_class_database(app_prefix + '_store_equivalence.txt')
    ctrl_equiv_db = equiv_class_database(app_prefix + '_control_equivalence.txt') 
    for pc_obj in pruning_db:
        pc = pc_obj.pc
        max_bits = pc_obj.max_bits
        ctrl_or_store = pc_obj.ctrl_or_store
        pilot = pc_obj.pilot
        inj_per_pc = 0
        pop = 0
        regs = []
        add_regs(regs, pc_obj.src_regs)
        add_regs(regs, pc_obj.mem_src_regs)
        add_regs(regs, pc_obj.dest_reg)
        for reg in regs:
            inj_per_pc += min(reg_bits_map[reg], max_bits)
        if ctrl_or_store == 'store':
            if pilot in store_equiv_db:
                pop = store_equiv_db.get_pop(pilot)
            else:
                ctrl_pilot = ctrl_equiv_db.get_pilot(pilot)
                pop = ctrl_equiv_db.get_pop(ctrl_pilot)
        else:
            pop = ctrl_equiv_db.get_pop(pilot)
        total_err_sites += pop * inj_per_pc
        def_use_total += pop * def_use_count_map.get(pc,0)
        if pc in addr_bound_count_map:
            addr_bound_total += pop * addr_bound_count_map[pc].get(pilot,0)
        if ctrl_or_store == 'store':
            store_inj_per_pc = pc_pilot_map[pc][pilot]
            store_equiv_total += pop * store_inj_per_pc
        else:
            ctrl_inj_per_pc = pc_pilot_map[pc][pilot]
            ctrl_equiv_total += pop * ctrl_inj_per_pc
            
    out_filename = app_prefix + '_pruning_stats.txt'
    out_filename2 = app_prefix + '_pruning_stats2.txt'
    outfile = open(out_filename, 'w')
    outfile2 = open(out_filename2, 'w')
    total_pruned = float(total_err_sites - total_inj)
    total_pruned_pct = (1 - total_inj / float(total_err_sites)) * 100
    store_pruned = (store_equiv_total - store_equiv_inj) / total_pruned * 100
    ctrl_pruned = (ctrl_equiv_total - ctrl_equiv_inj) / total_pruned * 100
    def_use_pruned = def_use_total / total_pruned * 100
    addr_bound_pruned = addr_bound_total / total_pruned * 100
    outfile.write('%d %d %f %f %f %f %f %f\n' % (total_inj, total_err_sites,\
            total_pruned_pct, store_pruned, ctrl_pruned, \
            def_use_pruned, addr_bound_pruned, \
            store_pruned+ctrl_pruned+def_use_pruned+addr_bound_pruned))
    outfile2.write('%d %d %d %d\n' % ((ctrl_equiv_total-ctrl_equiv_inj),\
            (store_equiv_total-store_equiv_inj), def_use_total, \
            addr_bound_total))
    outfile.close()
    outfile2.close()
                    
if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('Usage: python inj_create.py [app] [isa] (pop_coverage_size)')
        exit()

    collect_stats_flag = False  # enable if getting pruning effectiveness

    app_name = sys.argv[1]
    isa = sys.argv[2]
    pop_size = 100
    if len(sys.argv) == 4:
       pop_size = int(sys.argv[3]) 

    approx_dir = os.environ.get('APPROXGEM5')
    apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
    app_prefix = apps_dir + '/' + app_name

    pruning_db_file = app_prefix + '_pruning_database.txt'
    mem_bounds_file = app_prefix + '_mem_bounds.txt'

    pruning_db = [pc_info(None,None,None,in_string=i) for i in open(
        pruning_db_file).read().splitlines()[1:]]
    mem_bounds = map(int, open(
                 mem_bounds_file).read().splitlines()[1].split())
    mem_bound = max(mem_bounds)

    output = []
    store_equiv_db = equiv_class_database(app_prefix + '_store_equivalence.txt')
    ctrl_equiv_db = equiv_class_database(app_prefix + '_control_equivalence.txt') 
    pop_percent = float(pop_size)/100
    top_store_equiv_ids = store_equiv_db.get_top_pops(pop_percent)
    top_ctrl_equiv_ids = ctrl_equiv_db.get_top_pops(pop_percent)
    top_equiv_ids = set(top_store_equiv_ids + top_ctrl_equiv_ids)

 
    for item in pruning_db:
        pc = item.pc
        if pc not in pc_pilot_map:
            pc_pilot_map[pc] = {}
        ctrl_or_store = item.ctrl_or_store
        def_pc = item.def_pc
        do_inject = item.do_inject
        src_regs = item.src_regs
        mem_src_regs = item.mem_src_regs
        dest_reg = item.dest_reg
        is_mem = item.is_mem
        pilot = item.pilot
        if pop_size == 100 or pilot in top_equiv_ids:
            pc_pilot_map[pc][pilot] = 0
            max_bits = item.max_bits
            if do_inject:
                if src_regs is not None:
                    for src_reg in src_regs:
                        temp = create_inj(pc, isa, pilot, src_reg, max_bits)
                        inj_count = len(temp)
                        pc_pilot_map[pc][pilot] += inj_count
                        if ctrl_or_store == 'ctrl':
                            ctrl_equiv_inj += inj_count
                        else:
                            store_equiv_inj += inj_count
                        output += temp#create_inj(pc, isa, pilot, src_reg, max_bits)
                        
                if mem_src_regs is not None:
                    for mem_src_reg in mem_src_regs:
                        temp = create_inj(pc, isa, pilot, mem_src_reg, \
                                             max_bits, mem_bound)
                        inj_count = len(temp)
                        pc_pilot_map[pc][pilot] += inj_count
                        if ctrl_or_store == 'ctrl':
                            ctrl_equiv_inj += inj_count
                        else:
                            store_equiv_inj += inj_count
                        output += temp#create_inj(pc, isa, pilot, mem_src_reg, \
                                   #          max_bits, mem_bound)
                            
                # check destination register (pruning info found in def_pc)
                if def_pc is not None:
                    temp = create_def_inj(isa, pilot, pc, def_pc, max_bits)
                    inj_count = len(temp)
                    pc_pilot_map[pc][pilot] += inj_count
                    if ctrl_or_store == 'ctrl':
                        ctrl_equiv_inj += inj_count
                    else:
                        store_equiv_inj += inj_count
                    output += temp #create_def_inj(isa, pilot, pc, def_pc, max_bits)
    with open(app_prefix + '_inj_' + str(pop_size) + '_list.txt','w') as f:
        for inj in output:
            f.write('%s\n' % inj)
    total_inj = len(output)
    if collect_stats_flag:
        collect_stats(app_name, app_prefix, pruning_db, total_inj) 

