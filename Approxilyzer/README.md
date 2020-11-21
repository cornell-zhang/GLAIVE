# gem5-Approxilyzer

gem5-Approxilyzer is an open-source framework for instruction level approximation 
and resiliency software. gem5-Approxilyzer provides a systematic way to identify 
instructions that exhibit first-order approximation potential. It can also identify 
silent data corruption (SDC) causing instructions in the presence of single-bit errors. 
gem5-Approxilyzer employs static and dynamic analysis, in addition to heuristics, to reduce 
the run-time of finding approximate instructions and SDC-causing instructions by 3-6x 
orders of magnitude.

## Citation
If you use this work, please cite our paper published in the International Conference on Dependable Systems and Networks (DSN) 2019 where we developed and evaluated gem5-Approxilyzer.

R. Venkatagiri, K. Ahmed, A. Mahmoud, S. Misailovic, D. Marinov, C. W. Fletcher, S. V. Adve, “gem5-Approxilyzer: An Open-Source Tool for Application-Level Soft Error Analysis”, International Conference on Dependable Systems and Networks (DSN), 2019.
http://rsim.cs.illinois.edu/Pubs/19-DSN-gem5Approxilyzer.pdf

## gem5-Approxilyzer Setup Instructions
1. all dependencies for gem5 are required (see gem5 documentation) This includes the following:

  * gcc 4.8 or greater
  * python 2.7 or greater
  * SCons
  * SWIG 2.0.4 or greater
  * protobuf 2.1 or greater
  * M4

   On Ubuntu, the following commands should cover all of the requirements:
   
```
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install scons
sudo apt-get install python-dev
sudo apt-get install swig
sudo apt-get install libprotobuf-dev python-protobuf protobuf-compiler libgoogle-perftools-dev
sudo apt-get install m4
```
2. To build from the source code, go to the project's gem5 directory and run the following:
```
cd gem5
scons build/X86/gem5.fast -j${NUM_PROCS}
scons build/X86/gem5.opt -j${NUM_PROCS}
```

   Where `${NUM_PROCS}` is the number of available CPU cores.  
   
If interfacing with the simulator, build m5term by following gem5's [documentation](http://gem5.org/M5term).

## Downloading Disk Images
1. Download sample gem5 disk images [here](https://uofi.box.com/s/6h0ep96pbi5sexygmyobt778wyqfl3r6)
Create the following directory structure, or modify the paths in
gem5/configs/common/SysPaths.py: /dist/m5/system/disks
                            /dist/m5/system/binaries


## How to use gem5-Approxilyzer
1. Prepare your application. First, compile your application binaries with particular region-of-interest (ROI) indicators. In C/C++, this may look something like:
```
// ROI start
asm volatile("mov %rax,%rax");
...
// application code
...
// ROI end
asm volatile("mov %rbx,%rbx");
```
Once compiled, use **objdump** to disassemble the binary:
```
objdump -D -S ${BINARY_NAME} > ${BINARY_NAME}.dis
```
Note the PCs of the *beginning* and *end* of the ROI (`${MAIN_START}` and `${MAIN_END}` in step 6). 
Additionally, ensure the application has an error quality metric that can be evaluated from its output. Refer to `gem5/scripts/injections/detailed_app_leveL_analysis.pl` for an example, and insert the metric into that script.

Refer to gem5's [documentation](http://gem5.org/Disk_images) for adding applications to the gem5 disk image.

2. In the project's root directory, run `./setup.sh` to build additional directories and create the appropriate environment variable: `APPROXGEM5`. For any application being analyzed, make new directories by performing the following:
```
mkdir -p $APPROXGEM5/workloads/apps/x86/${APP_NAME}
mkdir -p $APPROXGEM5/workloads/checkpoint/x86/${APP_NAME}
```
3. Go to the project's gem5 directory, and setup initial disk image checkpoints. If you are unfimiliar with this process, the following sample command starts up the disk image from scratch:
```
build/X86/gem5.fast configs/example/fs.py \
--disk-image=$APPROXGEM5/dist/m5/system/disks/${DISK_IMAGE_NAME}.img \
--kernel=$APPROXGEM5/dist/m5/system/binaries/vmlinux-${VERSION}
```
This will create an `m5out` directory, which will store any checkpoints currently created.

4. Run your application within the simulator with the following command:
```
m5 checkpoint; [exec binary with args or run script]; m5 writefile [output filename]; m5 exit
```

IMPORTANT: if you are using the gem5-approxilyzer provided disk image, m5 writefile may not be the latest version. You can still use the above command, but replace `m5` with `/root/m5`.

Note the checkpoint's tick number once exiting the simulation.

5. Move the checkpoint from `m5out` to the corresponding app checkpoint directory:
```
mv $APPROXGEM5/gem5/m5out/ckpt.${CHECKPOINT_NUM} \
 $APPROXGEM5/workloads/x86/checkpoint/${APP_NAME}
```
Symbollicaly link the output file generated from step 4 to setup the "golden" output:
```
cd $APPROXGEM5/workloads/x86/checkpoint/${APP_NAME}
ln -s ln -s $PWD/${APP_OUTPUT_FILE} $PWD/{APP_NAME}.output
```

6. Parse the disassembly from step 1 to create an instruction database used for analysis:
```
cd $APPROXGEM5/gem5/scripts/relyzer
python inst_database.py $APPROXGEM5/workloads/x86/apps/${APP_DIS_FILE} \
 $APPROXGEM5/workloads/x86/apps/${APP_NAME}/{$APP_NAME}_parsed.txt
```
Generate a gem5 trace of the application and use gem5-Approxilyzer scripts to simplify the trace:
```
cd $APPROXGEM5/gem5/scripts/relyzer
./gen_exec_trace.sh x86 ${APP_NAME} ${DISK_IMAGE_NAME}
./gen_mem_trace.sh x86 ${APP_NAME} ${DISK_IMAGE_NAME}
python gen_simplified_trace.py ${app_name} ${MAIN_START} ${MAIN_END} x86
```

7. Run Relyzer analysis on the application:
```
./relyzer.sh ${APP_NAME} x86 ${POP_SIZE}
```
Note that `${POP_SIZE}` is optional, and by default it is set to 100. If you are analyzing larger apps, it is recommended to set `${POP_SIZE}` to 95 or 99. This analysis may take several hours to complete depending on the size of the application.

Relyzer analysis will generate an injection list located at `$APPROXGEM5/workloads/x86/apps/${APP_NAME}/${APP_NAME}_inj_list_${POP_SIZE}.txt`.

8. Perform error injection experiments with the following command:
```
cd $APPROXGEM5/gem5/scripts/injections
./run_jobs_parallel.sh ${INJ_LIST} x86 ${APP_NAME} ${APP_CKPT_NUM} ${GOLDEN_OUTPUT} ${NUM_PROCS} ${DISK_IMAGE}
```
The `${APP_CKPT_NUM}` should be set to 1 if no existing checkpoints are created and moved to the app's checkpoint directory from step 5. `${GOLDEN_OUTPUT}` should be set to the symbolic link created from step 5. Injections may take a long time to complete.

9. Combine all of the outcomes generated from step 8 and run gem5-Approxilyzer postprocessing analysis:
```
cd $APPROXGEM5/gem5/outputs/x86
cat ${APP_NAME}-* > ${APP_NAME}.outcomes_raw
cd $APPROXGEM5/gem5/scripts/relyzer
python postprocess.py ${APP_NAME} x86 
```
This will create the final outcome file of gem5-Approxilyzer analysis.
