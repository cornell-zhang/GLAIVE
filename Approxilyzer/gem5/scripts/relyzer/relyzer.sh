#!/bin/bash

# This script combines many steps of pre-processing into one (in progress)

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage : ./relyzer.sh [app_name] [isa] (pop_coverage_size)"
    exit 1
fi

app_name=$1
isa=$2
pop_size=100
if [ $# -eq 3 ]; then
    pop_size=$3
fi

apps_dir=$APPROXGEM5/workloads/$isa/apps/$app_name
curr_dir=$PWD

cd $APPROXGEM5/gem5/scripts/relyzer

if [ ! -f $apps_dir/${app_name}_parsed.txt ]; then
    python inst_database.py $apps_dir/${app_name}.dis $apps_dir/${app_name}_parsed.txt
fi

python control_equivalence.py $app_name $isa

python store_equivalence.py $app_name $isa

python def_use.py $app_name $isa

python bounding_address.py $app_name $isa

python pruning_database.py $app_name $isa

python inj_create.py $app_name $isa $pop_size

