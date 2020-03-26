#!/bin/bash

for subNum in {1..46}
do

echo "Start with subject $subNum"
   # generate a folder for each subject under betaData
   mkdir ~/traitNetwork_MVPA/betaseries/betaData/Subject"$subNum"

   for runNum in {1..4}
   do

     echo "Start with run $runNum"
     # locate root directory for each level-1 output that corresponding to each run
     modelDir="/home/bcheung/traitNetwork_MVPA/level-1/model/Subject"$subNum"/sub"$subNum"_run"$runNum"_MVPA.feat"
     # set output directory
     outputDir="/home/bcheung/traitNetwork_MVPA/betaseries/betaData/Subject"$subNum""

     # register betaseries from each run to a common space, which is the functional space after registration
     flirt -in  "$modelDir"/betaseries/ev1_LSA_.nii.gz -ref "$modelDir"/reg/example_func2standard -applyxfm -init "$modelDir"/reg/example_func2standard.mat -out "$outputDir"/sub"$subNum"_run"$runNum"_beta_std


   done
   echo "Finish registration"
   # concatenate data from all 4 runs
   fslmerge -t "$outputDir"/sub"$subNum"_betaMerge "$outputDir"/sub"$subNum"_run*_beta_std.nii.gz

   echo "Finish concatination"
   echo

done
