#!/bin/sh

# get the input arguments

# home directory for the social context project (no back lash at the end!)
home_dir=$1
# subject ID to start with
start_id=$2
# subject ID to end with
end_id=$3

#  locate the template file

echo Locate template file
templateFile="$home_dir""/MVPA_prep/FSL_level1/template/sub-01_task-friend_run-1.fsf"

#  allow access to read and write the template
chmod 777 $templateFile

echo
echo

#  loop through each subject

#  set subIDs as a sequence of 01 02 03 ... 46
for ((id=$start_id; id<=$end_id; id++))
do
  # convert the id to the correct format
  subNum=$(printf "%02d" $id)

  echo Start with sub $subNum
  #  create a folder for each subject under model
  mkdir "$home_dir"/MVPA_prep/FSL_level1//model/sub-"$subNum"
  #  create a folder called design under each subject folder
  mkdir "$home_dir"/MVPA_prep/FSL_level1//model/sub-"$subNum"/design
  #  set output directory for the .fsf file
  outputDir="$home_dir""/MVPA_prep/FSL_level1/model/sub-"$subNum"/design"
  echo

  # loop through each run within each subject
  for runNum in {1..4}
  do
    echo Start with run $runNum
    echo
    #echo "delete existing file"
    #  locate the existing file
    #previousFile="/home/bcheung/socialContext_MVPA/level-1/model/sub-"$subNum"_run-"$runNum"_MVPA.feat"

    #  delete the file
    #rm -r $previousFile
    #echo "delete""$previousFile"

    # extract the condition corresponding to the present run
    echo "extract the condition"
    condition=$(awk -v id="$id" -v runNum="$runNum" '($1 == id) && ($2 == runNum) {print $3}' "$home_dir"/MVPA_prep/FSL_level1/scripts/condition.txt)

    echo "modify the design file"

    #  replace the string in the template file with new subject number and run number to generate a new design file for each run
    #  find the file name for bold data for this specific run
    oldBold="sub-01_task-friend_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold"
    newBold=$(find "$home_dir"/bids_data/derivatives/fmriprep/sub-"$subNum"/func/ -type f -name "*run-"$runNum"_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz" -exec basename {} .nii.gz ';')
    sed -e 's:'$oldBold':'$newBold':g' -e 's:sub-01:sub-'$subNum':g' -e 's:run-1:run-'$runNum':g' -e 's:task-friend:task-'$condition':g' -e 's:/Users/BerniceCheung/Documents/Bernice/socialContext:'$home_dir':g'  <"$templateFile"> "$outputDir"/sub-"$subNum"_task-"$condition"_run-"$runNum".fsf

    echo
    echo "run FEAT level 1"

    #  feed the design file to FEAT to run level-1 process
    #feat "$outputDir"/sub-"$subNum"_run-"$runNum"_"$condition".fsf
  done

done
