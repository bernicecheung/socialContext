#!/bin/bash
#SBATCH --partition=ctn       ### Partition (like a queue in PBS)
#SBATCH --job-name=ROI_Fri      ### Job Name
#SBATCH --output=/projects/sanlab/kcheung3/socialContext/talapas_output/ROI_neuralRDM_sameCorr_fri.out         ### File in which to store job output
#SBATCH --error=/projects/sanlab/kcheung3/socialContext/talapas_output/ROI_neuralRDM_sameCorr_fri.err          ### File in which to store job error messages
#SBATCH --time=0-8:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --cpus-per-task=16               ### Number of CPU needed for the job
#SBATCH --mem=10G              ### Total memory
#SBATCH --account=sanlab      ### Account used for job submission


module load miniconda
conda activate nltools-bcheung3

python /projects/sanlab/kcheung3/socialContext/RSA/scripts/ROI_neuralRDM_sameCorr.py --rootDir /projects/sanlab/kcheung3/socialContext --context friend
