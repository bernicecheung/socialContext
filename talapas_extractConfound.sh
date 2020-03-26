#!/bin/bash
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --account=sanlab
#SBATCH --job-name=extractConfound     ### Job Name
#SBATCH --output=/projects/sanlab/kcheung3/socialContext/talapas_output/extractConfound.out         ### File in which to store job output
#SBATCH --error=/projects/sanlab/kcheung3/socialContext/talapas_output/extractConfound.err          ### File in which to store job error messages
#SBATCH --time=5-00:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=1               ### Number of CPU needed for the job
#SBATCH --mem=1G              ### Total memory

module load prl
module load python/2.7.13

python /home/kcheung3/sanlab/socialContext/MVPA_prep/scripts/extrConfound.py  \
  -maxSubID 1  \
  -maxRunNum 4  \
  -BIDS_dir /home/kcheung3/sanlab/socialContext/bids_data/ \
  -out_dir /home/kcheung3/sanlab/socialContext/MVPA_prep/confounds/ \
  -fd_threshold 0.5
