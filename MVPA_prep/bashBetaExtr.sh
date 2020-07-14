#!/bin/bash

# home directory for the social context project (no back lash at the end!)
home_dir=$1
# subject ID to start with
start_id=$2
# subject ID to end with
end_id=$3

# load python2 on talapas
module load python2/2.7.13

#  set a seqeunce of subject IDs
for ((id=$start_id; id<=$end_id; id++))
do
  # convert the id to the correct format (2 digit)
  subNum=$(printf "%02d" $id)

  echo "Start with subject $subNum"

  # loop through each run
  for runNum in {1..4}
  do
    echo "Start with run $runNum"

    # run the python script for extracting beta for each run (input: fsl level 1 output, number of EVs & types of GLMs (LSA or LSS))
    python "$home_dir"/MVPA_prep/scripts/pybetaseries_conf2019.py --fsldir "$home_dir"/MVPA_prep/FSL_level1/model/sub-"$subNum"/sub-"$subNum"_*_run-"$runNum".feat/ --conffile "$home_dir"/MVPA_prep/FSL_level1/confounds/sub-"$subNum"_run-"$runNum"_confound.txt --whichevs 1 -LSA
  done


done
