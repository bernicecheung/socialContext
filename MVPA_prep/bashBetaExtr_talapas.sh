#!/bin/bash
#SBATCH --partition=ctn        ### Partition (like a queue in PBS)
#SBATCH --account=sanlab
#SBATCH --job-name=socialContext_beta      ### Job Name
#SBATCH --output=/projects/sanlab/kcheung3/socialContext/talapas_output/beta.out         ### File in which to store job output
#SBATCH --error=/projects/sanlab/kcheung3/socialContext/talapas_output/beta.err          ### File in which to store job error messages
#SBATCH --time=5-00:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=4              ### Number of CPU needed for the job
#SBATCH --mem=8G              ### Total memory

chmod +777 /projects/sanlab/kcheung3/socialContext/MVPA_prep/scripts/bashBetaExtr.sh
sh /projects/sanlab/kcheung3/socialContext/MVPA_prep/scripts/bashBetaExtr.sh /projects/sanlab/kcheung3/socialContext 1 40
