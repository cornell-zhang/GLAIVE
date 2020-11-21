#===============================================================================
#
#         FILE: run_graphsage.py
#
#        USAGE:
#
#  DESCRIPTION:
#
#      OPTIONS: 
# REQUIREMENTS: 
#         BUGS: 
#        NOTES: 
#       AUTHOR: jiajia
#      CONTACT: 
# ORGANIZATION: ECE, Cornell University
#      VERSION: 
#      CREATED: 12-5-2020
#     REVISION: 
#    LMODIFIED: 
#===============================================================================


import os, sys
from argparse import ArgumentParser
from datetime import datetime as dt
from pprint import pprint as pp
import shutil, glob
#from pyfiglet import figlet_format, Figlet
import datetime

'''
python run_graphsage.py -a fft -l bit -n 5 
'''

def app(args):
    
    if not args:
        return []
    else:
        return args.split(',')
    

parser = ArgumentParser()
parser.add_argument('-a', "--apps", help='Target application names seperated by comma', \
        dest='targetapp', required=True)
parser.add_argument('-l', "--info_level", help='Target application architecture', \
        dest='info_level', default='bit')
parser.add_argument('-n', "--num_programs", help='Number of programs for dataset', \
        dest='num_progs', required=True)


args = parser.parse_args()

apps = app(args.targetapp)
level = args.info_level
num = args.num_progs 


for app in apps:
    gl_dir = os.environ.get('GRAPHLEARN')
    exe_dir = gl_dir 
    app = app + '_' + level
    if level == 'bit':
        ml_log_file =  exe_dir + 'ml' +'_' + app + '.log'
        gl_log_file =  exe_dir + 'gl' +'_' + app + '.log'
    elif level == 'inst':
        log_file =  exe_dir + 'ml' +'_' + app + '.log'
    
    #generate data
    gdata_path = exe_dir + 'gdata'
    os.chdir(gdata_path)
    cmd = 'python gen_data_' + level +'.py ' + app + ' ' + num
    status = os.system(cmd)
    
    if status != 0:
        print('gen data failure ' + app)
        exit(-1)
    
    #trainning and learning
    os.chdir(exe_dir)
    if level == 'bit' :
        cmd = 'python -m graphsage.jj_model -e 10 -b 256 -c 8 -a ' + app + ' > ' + gl_log_file
        status = os.system(cmd)
        if status != 0:
            print('gl training and predict failure ' + app)
            exit(-1)
        cmd = 'python ml_model_others.py ' + app + ' > ' + ml_log_file
        status = os.system(cmd)
        if status != 0:
            print('ml training and predict failure ' + app)
            exit(-1)
        
    elif level == 'inst':
        cmd = 'python regression_model_others.py ' + app + ' > ' + log_file
        status = os.system(cmd)
        if status != 0:
            print('inst-level training and predict failure ' + app)
            exit(-1)
    else:
        print('wrong input for learning configuration')
    
        
    #post-processing
    
    os.chdir(gdata_path)
    if level == 'bit':
        cmd = 'python gl_gen_post.py ' + app + ' '+ num
        status = os.system(cmd)   
        if status != 0:
            print('gl post handling failure' + app)
            exit(-1)
        cmd = 'python ml_gen_post.py ' + app + ' ' +num
        status = os.system(cmd)   
        if status != 0:
            print('ml post handling failure ' + app)
            exit(-1)
	
    elif level == 'inst': 
        cmd = 'python ml_inst_gen_post.py ' + app + ' ' + num  + ' rf'
        status = os.system(cmd)   
        if status != 0:
            print('inst-level post handling failure ' + app)
            exit(-1)

	cmd = 'python ml_inst_gen_post.py ' + app + ' ' + num  + ' svm'
        status = os.system(cmd)
        if status != 0:
            print('inst-level post handling failure ' + app)
            exit(-1)

    else:
        print('wrong input for learning configuration')
        
    
    #remove to free space
    cmd = 'rm ' + app +'_*'
    status = os.system(cmd)
    
    if status != 0:
        print('remove used data failure ' + app)
        exit(-1)
