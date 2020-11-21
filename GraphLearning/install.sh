#!/bin/bash

if grep -q GRAPHLEARN ~/.bashrc; then
    echo "GRAPHLEARN environment variable exists"
else
    last_dir=`echo $PWD | awk -F"/" '{print $NF}'`
    if [ "$last_dir" == "GraphLearning" ] && [ -f $PWD/.gitignore ]; then
        echo "export GRAPHLEARN=$PWD" >> ~/.bashrc
        source ~/.bashrc 
    else
        echo "Running script in incorrect directory!"
        exit 1
    fi
fi

# for logfile 
mkdir -p glog

# for graph leanring bit-level output
mkdir -p sdc_output


# for machine learning bit-level output
mkdir -p sdc_output_ml_bit
 
# for inst-level output
mkdir -p sdc_output_classic

