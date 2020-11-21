#===============================================================================
#
#         FILE: parse_log_3.py
#
#        USAGE:
#
#  DESCRIPTION:
#
#      OPTIONS: 
# REQUIREMENTS: 
#         BUGS: 
#        NOTES: 
#       AUTHOR: Debjit Pal
#      CONTACT: debjit.pal@cornell.edu
# ORGANIZATION: ECE, Cornell University
#      VERSION: 
#      CREATED: 22-11-2019
#     REVISION: 
#    LMODIFIED: Fri 22 Nov 2019 11:49:26 PM EST
#===============================================================================

import os, sys
from shutil import copyfile as cpf

gl_dir = os.environ.get('GRAPHLEARN')
SOURCE_PATH = gl_dir + '/data_app_source_bit'
DEST_PATH = gl_dir + '/num_source'

#SOURCE_PATH = 'path..../source_data/data_app_source_bit'
#DEST_PATH = 'path..../source_data/num_source'

files = [f for f in os.listdir(SOURCE_PATH) if f.endswith('.edgelist')]
files_sorted = sorted(files)
del files

counter = 0

mh = open('nfile_efile_glearn.map', 'w')
for file_ in files_sorted:
    name = file_[:file_.find('.')]
    cpf_name = str(counter)
    cpf(SOURCE_PATH + '/' + name + '.edgelist', DEST_PATH + '/' + cpf_name + '.edgelist')
    cpf(SOURCE_PATH + '/' + name + '.nodelist', DEST_PATH + '/' + cpf_name + '.nodelist')
    mh.write(name + '\t' + cpf_name + '\n')
    counter = counter + 1

mh.close()
