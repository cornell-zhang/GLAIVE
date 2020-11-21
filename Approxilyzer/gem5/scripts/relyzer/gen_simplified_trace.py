#!/usr/bin/python

# this script parses the compressed trace from gem5 and produces
# a simplified one used for Relyzer analysis.

import gzip
import io
import os
import sys

if len(sys.argv) != 5:
    print('Usage: python gen_simplified_trace.py [app_name] [main_start] [main_end] [isa]')
    exit()

app_name = sys.argv[1]

main_start = sys.argv[2]
main_end = sys.argv[3]
isa = sys.argv[4]

approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name


inst_db_file = app_prefix + '_parsed.txt'

inst_db_list = open(inst_db_file).read().splitlines()[1:]
app_pcs = set(['0x' + i.split()[0] for i in inst_db_list])



in_file_base = approx_dir + '/workloads/' + isa + '/checkpoint/' + \
               app_name + '/' + app_name
in_file_dump = in_file_base + '_dump.gz'

start_recording = False
stop_recording = False


inst_num_list = []
inst_num_pc_map = {}
inst_num_map = {}

apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name

def get_out_string(curr_entry, curr_entry_mem, curr_entry_mem_addr):
    '''
    returns the entry in string format (tick, pc, (r/w, mem_addr)...)
    '''
    out_string = ' '.join(curr_entry)
    for i,mem in enumerate(curr_entry_mem):
        out_string += ' ' + ' '.join([mem,curr_entry_mem_addr[i]]) 
    return out_string

if isa == 'x86':
    start_recording = False
    stop_recording = False
    in_file_dump_micro = in_file_base + '_dump_micro.gz'
    in_file_mem_dump = in_file_base + '_mem_dump.gz'
    # TODO: rename file for simplified trace (too verbose)
    out_filename = app_prefix + '_clean_dump_parsed_merged.txt'
    
    dis_list = gzip.open(in_file_dump_micro)
    dis_io = io.BufferedReader(dis_list)
    mem_list = gzip.open(in_file_mem_dump)
    mem_io = io.BufferedReader(mem_list)

    pc = None
    prev_pc = pc
    curr_entry = []
    curr_entry_mem = []
    curr_entry_mem_addr = []
    mem_file_done = False
    outfile = open(out_filename,'w')
    mem_tick = 0
    mem_line = ''
    mem_entry = []

    for line in dis_io:
        if 'system.cpu' in line:
            temp = line.split()
            tick = int(temp[0].rstrip(': '))
            temp_pc_info = temp[2].split('.')
            pc = temp_pc_info[0]
            if pc == main_start:
                start_recording = True
            if pc == main_end:
                stop_recording = True
            if pc in app_pcs and pc != prev_pc and start_recording:
                if stop_recording:
                    # print final entry
                    out_string = get_out_string(curr_entry, curr_entry_mem, curr_entry_mem_addr)
                    if out_string != '':
                        outfile.write('%s\n' % out_string)
                    break
                out_string = get_out_string(curr_entry, curr_entry_mem, curr_entry_mem_addr)
                if out_string != '':
                    outfile.write('%s\n' % out_string)
                # clear previous entry and start new one
                curr_entry = []
                curr_entry_mem = []
                curr_entry_mem_addr = [] 
                curr_entry.append(str(tick))
                curr_entry.append(pc)
            # TODO simplify conditional statements
            if not mem_file_done:
                while mem_tick <= tick:
                    if start_recording and pc in app_pcs:
                        if mem_tick == tick:
                            if mem_entry[4] == 'cpu.data':
                                read_or_write = mem_entry[2]
                                if 'Read' in read_or_write or 'Write' in read_or_write:
                                    address = mem_entry[10] # location in gem5 tracer
                                    curr_entry_mem.append(read_or_write)
                                    curr_entry_mem_addr.append(address)
                    mem_line = mem_io.readline()
                    if mem_line is None:
                        mem_file_done = True
                        break
                    mem_entry = mem_line.split()
                    if len(mem_entry) > 0:
                        mem_tick = int(mem_entry[0].rstrip(': '))
            
            if pc in app_pcs:
                prev_pc = pc
    dis_list.close()
    mem_list.close()
    outfile.close()
