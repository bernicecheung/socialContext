#!/bin/bash
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --account=sanlab
#SBATCH --job-name=socialContext_fMRIprep      ### Job Name
#SBATCH --output=fMRIprep_1.out         ### File in which to store job output
#SBATCH --error=fMRIprep_1.err          ### File in which to store job error messages
#SBATCH --time=5-00:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=8               ### Number of CPU needed for the job
#SBATCH --mem=10G              ### Total memory


chmod +x /projects/sanlab/kcheung3/socialContext/fMRIPrep/job_fmriprep.sh
sh /projects/sanlab/kcheung3/socialContext//fMRIPrep/job_fmriprep.sh
