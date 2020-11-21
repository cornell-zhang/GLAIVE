import os, sys
from argparse import ArgumentParser
from datetime import datetime as dt
from pprint import pprint as pp
import shutil, glob
#from pyfiglet import figlet_format, Figlet
import datetime

'''
python run_approxilyzer.py -a min_max -r x86 -d x86root-parsec.img -k vmlinux-4.9.113 -n 8
'''

def run_approxilyzer(apps, config):

    for app in apps:
        log_file = config['GEM5'] + '/gem5log/' + app +'_time.log'
        with open(log_file,'w') as f:
        #figlet_
		
        	print('Step 1')
        	f.write('Step 1-to 7 for pre-analysis--')
        	starttime = datetime.datetime.now()
        	f.write('start time is : %s ' %starttime)
        	MAIN_START, MAIN_END = step_1(app, config['WORKLOAD_APPS'])
        #figlet_
        	print('Step 2')
        	step_2(app, config['WORKLOAD_APPS'], config['WORKLOAD_CPT'])
        	step_3_and_4_and_5(app, config['GEM5_FAST'], config['GEM5'], config['DISK'], config['KERNEL'], \
                	config['DISK_NAME'], config['KERNEL_NAME'], config['SCRIPTS'], config['WORKLOAD_CPT'])
        	step_6_and_7(app, config['WORKLOAD_APPS'], config['ARCH'].lower(), config['GEM5'], \
                	MAIN_START, MAIN_END, config['DISK_NAME'])
        	endtime = datetime.datetime.now()
        	f.write('start time is : %s' %endtime)
        	f.write('runtime is : %s \n' %((endtime - starttime).seconds))        
                
        
        #figlet_
        	print('Step 8')
        	f.write('Step 8 for fault injection--')
        	starttime = datetime.datetime.now()
        	f.write('start time is : %s' %starttime)
        	step_8(app, config['GEM5'], config['WORKLOAD_APPS'], config['ARCH'].lower(), config['NUM_PROCS'], \
                	config['DISK_NAME'])
        	endtime = datetime.datetime.now()
        	f.write('start time is : %s' %endtime)
        	f.write('runtime is : %s \n' %((endtime - starttime).seconds)) 

        
        #figlet_	
        	print('Step 9')
        	f.write('Step 9 for post analysis--')
        	starttime = datetime.datetime.now()
        	f.write('start time is : %s' %starttime)
        	step_9(app, config['GEM5'], config['ARCH'].lower())
            	endtime = datetime.datetime.now()
            	f.write('start time is : %s' %endtime)
            	f.write('runtime is : %s \n' %((endtime - starttime).seconds)) 
        	
        #figlet_
            	print('construct graph')
        	f.write(' graph construction for graph learning--')
        	starttime = datetime.datetime.now()
        	f.write('start time is : %s' %starttime)
            	consGraph(app, config['GEM5'],config['ARCH'].lower())
            	endtime = datetime.datetime.now()
        	f.write('start time is : %s' %endtime)
        	f.write('runtime is : %s \n' %((endtime - starttime).seconds))
	f.close()
    return

def step_1(app, wadir):
    # NOTE: Checked
    ''' 
    cmd = 'gcc -o ' + os.path.join(wadir, app, app) + ' -gdwarf-2 ' + os.path.join(wadir, app, app + '.c')
    status = os.system(cmd)
    if status != 0:
        print('Compilation of app: ' + app + ' failed')
        exit(-1)
    
    cmd = 'objdump -D -S ' + os.path.join(wadir, app, app) + ' > ' + os.path.join(wadir, app, app + '.dis')
    status = os.system(cmd)
    if status != 0:
        print('Object dump for app: ' + app + ' failed')
        exit(-1)
    '''
    f = open(os.path.join(wadir, app, app + '.dis'), 'r')
    l = f.readlines()
    f.close()
    ROI_idx = [idx for idx in range(len(l)) if 'ROI' in l[idx]]
    MAIN_START = l[ROI_idx[0] + 2].split()[0][:-1]
    MAIN_END = l[ROI_idx[1] + 2].split()[0][:-1]
    

    #MAIN_START = l[ROI_idx[0] + 2].split()[0][:-1]
    #MAIN_END = l[ROI_idx[1] - 1].split()[0][:-1]
    
    return MAIN_START, MAIN_END

def step_2(app, wadir, wcdir):

    if not os.path.isdir(os.path.join(wadir, app)):
        print('Workload app directory for app: ' + app + ' does not exist')
        exit(-1)

    if not os.path.isdir(os.path.join(wcdir, app)):
        print('Workload checkpoint directory for app: ' + app + ' does not exist')
        exit(-1)

    print('Both app and checkpoint directory for app: ' + app + ' exist')

    return

def step_3_and_4_and_5(app, gem5_fast, gem5, disk, kernel, disk_name, kernel_name, scripts, wcdir):

    old_dir = os.getcwd()

    os.chdir(gem5)

    #figlet_
    print('Step 3')
    
    cmd = gem5_fast + ' ' + os.path.join(gem5, 'configs/example', 'fs.py') + \
            ' --disk-image=' + os.path.join(disk, disk_name) + \
            ' --kernel=' + os.path.join(kernel, kernel_name) + \
            ' --script ' + os.path.join(scripts, app + '.rcS')

    status = os.system(cmd)
    
    if status != 0:
        print('Checkpoint creation failed for app: ' + app)
        exit(-1)
    
    # NOTE: Needs to be fixed ASAP
    #figlet_
    print('Step 4')
    d = os.path.join(gem5, 'm5out')
    dirs = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]
    cpt_dir_name = dirs[0][dirs[0].rfind('/') + 1:]
    if not os.path.isdir(os.path.join(wcdir, app, cpt_dir_name)):
        os.mkdir(os.path.join(wcdir, app, cpt_dir_name))
    else:
        shutil.rmtree(os.path.join(wcdir, app, cpt_dir_name))
        os.mkdir(os.path.join(wcdir, app, cpt_dir_name))

    move_file_src_dest(dirs[0], os.path.join(wcdir, app, cpt_dir_name))
    if(app == 'sobel' or app == 'kmeans'):	 
    	src_file = os.path.join(gem5, 'm5out', 'output.pgm')
    elif (app == 'jpeg'):
	src_file = os.path.join(gem5, 'm5out', 'output.jpg')
    else:
	src_file = os.path.join(gem5, 'm5out', 'output.txt')
    dest_file = os.path.join(wcdir, app, app + '.output')

    #figlet_
    print('Step 5')
    if os.path.islink(dest_file):
        os.unlink(dest_file)

    os.symlink(src_file, dest_file)

    os.chdir(old_dir)

    return

def step_6_and_7(app, wadir, arch, gem5, MAIN_START, MAIN_END, disk_name):

    old_dir = os.getcwd()

    #figlet_
    print('Step 6')
    os.chdir(os.path.join(gem5, 'scripts/relyzer'))

    cmd = 'python inst_database.py ' + os.path.join(wadir, app, app + '.dis') + \
            ' ' + os.path.join(wadir, app, app + '_parsed.txt')
    status = os.system(cmd)
    if status != 0:
        print('Creation of instruction data based failed for app: ' + app)
        exit(-1)

    cmd = 'sh gen_exec_trace.sh' + ' ' + arch + ' ' + app + ' ' + disk_name
    status = os.system(cmd)
    if status != 0:
        print('Execution trace generation failed for app: ' + app)
        exit(-1)

    cmd = 'sh gen_mem_trace.sh' + ' ' + arch + ' ' + app + ' ' + disk_name
    status = os.system(cmd)
    if status != 0:
        print('Memory trace generation failed for app: ' + app)
        exit(-1)

    cmd = 'python gen_simplified_trace.py' + ' ' + app + ' ' + '0x' + MAIN_START + ' ' + '0x' + MAIN_END + ' ' + arch 
    status = os.system(cmd)
    if status != 0:
        print('Simplified trace generation failed for app: ' + app)
        exit(-1)

    #figlet_
    print('Step 7')
    cmd = 'sh relyzer.sh' + ' ' + app + ' ' + arch + ' 100' 
    status = os.system(cmd)
    if status != 0:
        print('Relyzer analysis failed for app: ' + app)
        exit(-1)

    os.chdir(old_dir)

    return

def step_8(app, gem5, wadir, arch, num_procs, disk_name):

    old_dir = os.getcwd()

    os.chdir(os.path.join(gem5, 'scripts/injections'))

    cmd = 'sh run_jobs_parallel.sh' + ' ' + os.path.join(wadir, app, app + '_inj_100_list.txt') + ' ' + \
            arch + ' ' + app + ' 1 ' + app + '.output ' + num_procs + ' ' + disk_name
    status = os.system(cmd)
    if status != 0:
        print('Faul injection failed for the app: ' + app)
        exit(-1)

    os.chdir(old_dir)

    return

def step_9(app, gem5, arch):

    old_dir = os.getcwd()

    os.chdir(os.path.join(gem5, 'outputs', arch))

    cmd = 'cat ' + app + '-* > ' + app + '.outcomes_raw'
    status = os.system(cmd)
    if status != 0:
        print('Concatenating raw outputs failed for the app: ' + app)
        exit(-1)

    os.chdir(os.path.join(gem5, 'scripts/relyzer'))
    
    cmd = 'python postprocess.py' + ' ' + app + ' ' + arch
    status = os.system(cmd)
    if status != 0:
        print('Posprocessing raw data failed for app: ' + app)
        exit(-1)

    os.chdir(old_dir)

    return

def consGraph(app, gem5, arch):

    old_dir = os.getcwd()

    #figlet_
    print('construct graph')
    os.chdir(os.path.join(gem5, 'scripts/relyzer'))

    cmd = 'python inst_dep_gen.py ' + ' ' + app +  ' ' + arch
    status = os.system(cmd)
	
    if status != 0:
        print('Creating instruction dependence for app: ' + app)
        exit(-1)

    cmd = 'python bb_dep_gen.py ' + ' ' + app +  ' ' + arch
    status = os.system(cmd)
	
    if status != 0:
        print('Creating basic block dependence for app: ' + app)
        exit(-1)

    cmd = 'python error_graph_pro.py ' + ' ' + app +  ' ' + arch
    status = os.system(cmd)
	
    if status != 0:
        print('Creating error graph at four levels for app: ' + app)
        exit(-1)

    os.chdir(old_dir)

    return

def move_file_src_dest(srcDir, dstDir):
    if os.path.isdir(srcDir) and os.path.isdir(dstDir) :
        for filePath in glob.glob(srcDir + '/*'):
            shutil.move(filePath, dstDir);
    else:
        print("srcDir & dstDir should be Directories") 

    return

def main(apps, arch, disk, kernel, num_procs):

    # Setting up bash script and workload folder hierarchy for the Approxilyzer run
    status = os.system('sh install.sh')
    if status == 0:
        os.environ['APPROXGEM5'] = os.getcwd()
    else:
        exit(-1)
    
    
    
    # To store all pertinent information
    config = {}
    # Setting up APPROXGEM5 environment variable for everything else going forward
    APPROXGEM5 = os.getenv('APPROXGEM5')
    
    config['GEM5'] = os.path.join(APPROXGEM5, 'gem5')
    config['KERNEL'] = os.path.join(APPROXGEM5, 'dist/m5/system/binaries')
    config['DISK'] = os.path.join(APPROXGEM5, 'dist/m5/system/disks')
    config['SCRIPTS'] = os.path.join(APPROXGEM5, 'checkpoint_scripts')
    config['ARCH'] = arch.upper()
    config['DISK_NAME'] = disk
    config['KERNEL_NAME'] = kernel
    config['NUM_PROCS'] = num_procs
    config['WORKLOAD_APPS']  = os.path.join(APPROXGEM5, 'workloads', arch, 'apps')
    config['WORKLOAD_CPT']  = os.path.join(APPROXGEM5, 'workloads', arch, 'checkpoint')
    
    GEM5_FAST = os.path.join(config['GEM5'], 'build', config['ARCH'], 'gem5.fast')
    GEM5_OPT = os.path.join(config['GEM5'], 'build', config['ARCH'], 'gem5.opt')

    if not os.path.isfile(GEM5_FAST) or not os.access(GEM5_FAST, os.X_OK):
        print('gem5.fast executable is not available in the path ' + os.path.join(config['GEM5'], 'build'))
        exit(-1)
    else:
        config['GEM5_FAST'] = GEM5_FAST

    if not os.path.isfile(GEM5_OPT) or not os.access(GEM5_OPT, os.X_OK):
        print('gem5.opt executable is not available in the path ' + os.path.join(config['GEM5'], 'build'))
        exit(-1)
    else:
        config['GEM5_OPT'] = GEM5_OPT
        
    

    run_approxilyzer(apps, config)
    
    return
'''
def figlet_print(text):
    (width, height) = getTerminalSize()
    f = Figlet(font='slant', direction=1, justify='center', width=width)
    print(f.renderText(text))
    return
'''
def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass

    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

def app(args):
    
    if not args:
        return []
    else:
        return args.split(',')
    

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-a', "--apps", help='Target application names seperated by comma', \
            dest='targetapp', required=True)
    parser.add_argument('-r', "--architecture", help='Target application architecture', \
            dest='arch', default='x86')
    parser.add_argument('-d', "--disk_image", help='Disk image name', \
            dest='disk', required=True)
    parser.add_argument('-k', "--kernel_binary", help='Kernel binary name', \
            dest='kernel', required=True)
    parser.add_argument('-n', "--num_procs", help='Number of processors to be used for parallel fault injection', \
            dest='num_procs', required=True)


    args = parser.parse_args()

    apps = app(args.targetapp)

    main(apps, args.arch, args.disk, args.kernel, args.num_procs)
