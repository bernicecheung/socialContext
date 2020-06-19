#!/bin/bash

for subNum in {1..42}
do

echo "Start with subject $subNum"

   for runNum in {1..4}
   do
     echo "Start with run $runNum"

     python ~/traitNetwork_MVPA/betaseries/script/pybetaseries_conf2019.py --fsldir ~/traitNetwork_MVPA/level-1/model/Subject"$subNum"/sub"$subNum"_run"$runNum"_MVPA.feat/ --conffile ~/traitNetwork/Subject"$subNum"/bold/run"$runNum"/QA_2/confound2.txt --whichevs 1 -LSA
   done


done
