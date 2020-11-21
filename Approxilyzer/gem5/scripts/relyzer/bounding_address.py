#!/usr/bin/python

# This script computes the address bounds given the memory profile.

import os
import sys

if len(sys.argv) != 3:
    print('Usage: python bounding_address.py [app_name] [isa]')
    exit()

app_name = sys.argv[1]
isa = sys.argv[2]

approx_dir = os.environ.get('APPROXGEM5')
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name

trace_file = app_prefix + '_clean_dump_parsed_merged.txt'

min_addr = None
max_addr = None

with open(trace_file) as trace:
    for line in trace:
        temp = line.split()
        if len(temp) > 2:
            addr = int(temp[3],16)
            if min_addr is None:
                min_addr = addr
                max_addr = addr
            if addr < min_addr:
                min_addr = addr
            if addr > max_addr:
                max_addr = addr

print('Min addr: 0x%x' % min_addr)
print('Max addr: 0x%x' % max_addr)

min_count = 0
max_count = 0

min_mask = 1 << 63
max_mask = min_mask

for i in range(64):  # maximum number of bits affected
    if ((min_mask >> i) & min_addr) > 0:
        min_count = i
        break
for i in range(64):
    if ((max_mask >> i) & max_addr) > 0:
        max_count = i
        break
lower_limit = 64 - min_count
upper_limit = 64 - max_count
print('min bits not touched: %d' % min_count)
print('max bits not touched: %d' % max_count)

output_file = app_prefix + '_mem_bounds.txt'
output = open(output_file, 'w')
output.write('lower_limit upper_limit\n')
output.write('%s %s\n' % (lower_limit,upper_limit))
output.close()

