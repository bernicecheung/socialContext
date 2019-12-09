#!/bin/bash
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --account=sanlab
#SBATCH --job-name=extractFD     ### Job Name
#SBATCH --output=extractFD.out         ### File in which to store job output
#SBATCH --error=extractFD.err          ### File in which to store job error messages
#SBATCH --time=5-00:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=1               ### Number of CPU needed for the job
#SBATCH --mem=1G              ### Total memory

module load prl
module load python/2.7.13

python /home/kcheung3/sanlab/socialContext/fMRIPrep/qc/extractFD.py
