#!/bin/bash
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --job-name=socialContext_Feat_level1      ### Job Name
#SBATCH --output=/projects/sanlab/kcheung3/socialContext/talapas_output/feat_level1.out         ### File in which to store job output
#SBATCH --error=/projects/sanlab/kcheung3/socialContext/talapas_output/feat_level1.err          ### File in which to store job error messages
#SBATCH --time=0-01:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=8               ### Number of CPU needed for the job
#SBATCH --mem=100G              ### Total memory
#SBATCH --account=sanlab      ### Account used for job submission

chmod +777 /projects/sanlab/kcheung3/socialContext/MVPA_prep/FSL_level1/scripts/Feat-1.sh
/projects/sanlab/kcheung3/socialContext/MVPA_prep/FSL_level1/scripts/Feat-1.sh /projects/sanlab/kcheung3/socialContext 1 2
