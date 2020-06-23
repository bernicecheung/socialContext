#!/bin/bash

# set task parameters
# subject ID to start with
start_id=$1
# subject ID to end with
end_id=$2

module load fsl/5.0.10

for ((id=$start_id; id<=$end_id; id++))
do
  # convert the id to the correct format
  subNum=$(printf "%02d" $id)

  for runNum in {1..4}
  do

    sbatch --partition=ctn \
	 	--job-name=socialContext_Feat_level1 \
	 	--output=/projects/sanlab/kcheung3/socialContext/talapas_output/feat_level1_sub-"$subNum"_run-"$runNum".out \
    --error=/projects/sanlab/kcheung3/socialContext/talapas_output/feat_level1_sub-"$subNum"_run-"$runNum".err \
    --time=1-00:00:00 \
    --cpus-per-task=1 \
	 	--mem-per-cpu=8G \
	 	--account=sanlab \
    feat /projects/sanlab/kcheung3/socialContext/MVPA_prep/FSL_level1/model/sub-"$subNum"/design/sub-"$subNum"_*_run-"$runNum".fsf

  done  # run loop

done # subject loop
