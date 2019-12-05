#!/bin/bash
#
# This batch file calls on your subject
# list (named subject_list.txt). And
# runs the job_fmriprep.sh file for
# each subject. It saves the ouput
# and error files in their specified
# directories.
#

# Set your directories
group_dir=/projects/sanlab
user_dir=/projects/sanlab/kcheung3
container=shared/containers/fmriprep-1.4.0.simg
freesurferlicense=/projects/sanlab/shared/containers/license.txt
study=socialContext

# Set subject list
sublist=`cat fmriprep_list.txt`

# Submit fmriprep jobs for each subject
for sub in ${sublist}; do

SUBID=`echo $sub|awk '{print $1}' FS=,`
SESSID=`echo $sub|awk '{print $2}' FS=,`

sbatch --export ALL,subid=${SUBID},group_dir=${group_dir},user_dir=${user_dir},study=${study},container=${container},freesurferlicense=${freesurferlicense} \
        --job-name ${SUBID}_fMRIprep \
        --partition=ctn \
        --account=sanlab \
	--mem=20G \
  --time=1-00:00:00 \
  --cpus-per-task=16 \
	-o ${user_dir}/${study}/fMRIPrep/output/${SUBID}_fmriprep_output.txt \
	-e ${user_dir}/${study}/fMRIPrep/output/${SUBID}_fmriprep_error.txt \
	job_fmriprep.sh
done
