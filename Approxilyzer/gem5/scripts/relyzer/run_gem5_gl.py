import os, sys
from argparse import ArgumentParser
from datetime import datetime as dt
from pprint import pprint as pp
import shutil, glob
#from pyfiglet import figlet_format, Figlet
import datetime

'''
python run_gem5_gl.py -a radix -l inst 
python run_gem5_gl.py -a radix -l bit 
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


args = parser.parse_args()

apps = app(args.targetapp)
level = args.info_level
#num = args.num_progs
src_dir = os.environ.get('GRAPHLEARN')
gem5_dir= os.environ.get('APPROXGEM5') + '/gem5/scripts/relyzer/' 
dest_dir = os.environ.get('APPROXGEM5') + '/workloads/x86/apps/'
 
for app in apps:
    
   
    
    app1 = app + '_' + level  
    os.chdir(gem5_dir)
    
    if level == 'bit':
        # cp result from src to dest
	gl_src_file =  src_dir + 'sdc_output' +'/' + app1 + '_post.txt'
        gl_dest_file = dest_dir + app +'/' + app1 + '_post.txt'
        cmd = 'cp ' + gl_src_file + ' ' + gl_dest_file
        status = os.system(cmd)
        if status != 0:
            print('cp data in gl failure ' + app1)
            exit(-1)

        bit_rf_src_file =  src_dir + 'sdc_output_ml_bit' +'/' + app1 + '_post_rf.txt'
        bit_rf_dest_file =  dest_dir + app +'/' + app1 + '_post_rf.txt'
        cmd = 'cp ' + bit_rf_src_file + ' ' + bit_rf_dest_file
        status = os.system(cmd)
        if status != 0:
            print('cp data in rf_bit faigem5_dirlure ' + app1)
            exit(-1)
        
        bit_mlpc_src_file =  src_dir + 'sdc_output_ml_bit' +'/' + app1 + '_post_mlpc.txt'
        bit_mlpc_dest_file =  dest_dir + app +'/' + app1 + '_post_mlpc.txt'
        cmd = 'cp ' + bit_mlpc_src_file + ' ' + bit_mlpc_dest_file
        status = os.system(cmd)
        if status != 0:
            print('cp data in mlpc_bit failure ' + app1)
            exit(-1)
        
	
	#call sdc_comp
	
	print('this is for %s comp_sdc under graph learning ' % app)
        cmd = 'python comp_sdc.py ' + app + ' ' + 'x86' + ' ' + 'gl'
        status = os.system(cmd)
        if status != 0:
            print('sdc comp in gl_bit failure ' + app1)
            exit(-1)
        
    
	print('this is for %s comp_sdc under random forest learning ' % app)
        cmd = 'python comp_sdc.py ' + app + ' ' + 'x86' + ' ' + 'rf'
        status = os.system(cmd)
        if status != 0:
            print('sdc comp in rf_bit failure ' + app1)
            exit(-1)

        print('this is for %s comp_sdc under MLP learning ' % app)
        cmd = 'python comp_sdc.py ' + app + ' ' + 'x86' + ' ' + 'mlpc'
        status = os.system(cmd)
        if status != 0:
            print('sdc comp in mlpc_bit failure ' + app1)
            exit(-1)
        
	# call coverage_comp
        log_file = src_dir + 'glog/' + app + '.log'
        cmd = 'python sdc_coverage.py ' + app + ' ' + '5' + ' ' + '105' + ' > ' + log_file
        status = os.system(cmd)
        if status != 0:
            print('coverage comp for all methods failure ' + app)
            exit(-1)
        
    elif level == 'inst':
        inst_rf_src_file =  src_dir + 'sdc_output_classic' +'/' + app1 + '_rf.sdclist'
        inst_rf_dest_file =  dest_dir + app +'/' + app1 + '_rf.sdclist'
        cmd = 'cp ' + inst_rf_src_file + ' ' + inst_rf_dest_file
        status = os.system(cmd)
        if status != 0:
            print('cp data in inst_rf failure ' + app1)
            exit(-1)
        
        inst_svm_src_file =  src_dir + 'sdc_output_classic' +'/' + app1 + '_svm.sdclist'
        inst_svm_dest_file =  dest_dir + app +'/' + app1 + '_svm.sdclist'
        cmd = 'cp ' + inst_svm_src_file + ' ' + inst_svm_dest_file
        status = os.system(cmd)
        if status != 0:
            print('cp data in inst_svm failure ' + app1)
            exit(-1)
        
    
    
    
    
