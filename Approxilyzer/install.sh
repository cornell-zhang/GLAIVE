#!/bin/bash

if grep -q APPROXGEM5 ~/.bashrc; then
    echo "APPROXGEM5 environment variable exists"
else
    last_dir=`echo $PWD | awk -F"/" '{print $NF}'`
    if [ "$last_dir" == "Approxilyzer" ] && [ -f $PWD/.gitignore ]; then
        echo "export APPROXGEM5=$PWD" >> ~/.bashrc
        source ~/.bashrc 
    else
        echo "Running script in incorrect directory!"
        exit 1
    fi
fi

mkdir -p workloads/x86/apps
mkdir -p workloads/x86/checkpoint
mkdir -p gem5/outputs/x86
mkdir -p gem5/logfile


