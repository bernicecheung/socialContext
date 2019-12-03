#!/bin/bash
#
# This script runs fmriprep on subjects located in the
# BIDS directory and saves ppc-ed output and motion confounds
# in the derivatives folder.

# Set directories
group_dir=/projects/sanlab/shared
user_dir=/projects/sanlab/kcheung3
study=socialContext
container=containers/fmriprep-1.4.0.simg
freesurferlicense=/projects/sanlab/shared/containers/license.txt
bids_dir=${user_dir}/${study}/bids_data
derivatives=${bids_dir}/derivatives
working_dir=${derivatives}/scratch
image=${group_dir}/${container}

# Set subject ID
subid=01

echo -e \nFmriprep on ${subid}
echo -e \nContainer: ${image}
echo -e \nSubject directory: ${bids_dir}

# Load packages
module load singularity

# Create working directory
if [ ! -d ${working_dir} ]; then
	mkdir -p ${working_dir}
fi

# Run container using singularity
cd ${bids_dir}


echo -e \nStarting on: ${subid}
echo -e \n

singularity run --bind ${group_dir}:${group_dir} ${image} ${bids_dir} ${derivatives} participant \
				--participant_label ${subid} \
				-w ${working_dir} \
				--nthreads 1 \
				--mem-mb 100000 \
				--fs-license-file ${freesurferlicense} \
				--fs-no-reconall \
				--fd-spike-threshold 0.2 \


echo -e \n
echo -e \ndone
echo -e \n-------------------------------

# clean tmp folder
/usr/bin/rm -rvf /tmp/fmriprep*
