#!/bin/bash

# credit to stackoverflow PSkocik for parallel implementation

if [ $# -lt 6 ] || [ $# -gt 7 ]; then
    echo "Usage: ./run_jobs_parallel.sh [inj_list] [isa] [app] [app_ckpt_num] [golden_app_output] [num_procs] (disk_image for x86)"
    exit 1
fi

inj_list=$1
isa=$2
app=$3
app_ckpt_num=$4
golden_output=$5
num_procs=$6

disk_image=""
if [ $# -eq 7 ]; then
    disk_image=$7
fi

run_script=""
if [ "$isa" == "x86" ]; then
    if [ $# -ne 7 ]; then
        echo "Error: need disk_image"
        exit 1
    fi
    run_script=$APPROXGEM5/gem5/scripts/injections/run_injection_x86.sh
elif [ "$isa" == "sparc" ]; then
    run_script=$APPROXGEM5/gem5/scripts/injections/run_injection_sparc.sh
fi

open_sem(){
    mkfifo pipe-$$
    exec 3<>pipe-$$
    rm pipe-$$
    local i=$1
    for((;i>0;i--)); do
        printf %s 000 >&3
    done
}
run_with_lock(){
    local x
    read -u 3 -n 3 x && ((0==x)) || exit $x
    (
    "$@" 
    printf '%.3d' $? >&3
    )&
}

id=1
N=$num_procs
open_sem $N
while IFS= read -r inj; do
    if [ "$isa" == "x86" ]; then
        run_with_lock $run_script $app $inj $app_ckpt_num $golden_output $disk_image $id
    elif [ "$isa" == "sparc" ]; then
        run_with_lock $run_script $app $inj $app_ckpt_num $golden_output $id
    fi
    ((id++))
done < "$inj_list"
