#!/usr/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: ./run_injector_test.sh [app_dir] [disk_image]"
    exit 1
fi

app=$1
disk_image=$2

if [ $APPROXGEM5 -eq "" ]; then
    echo "Environment variables not set! Rerun install.sh (see README)"
    exit 1
fi

for test_file in $app; do
    injection=`cat $test_file`
    #TODO finish
    #$APPROXGEM5/gem5/scripts/run_injection.sh $injection 
    
done
