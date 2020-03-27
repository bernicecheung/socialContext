#!/bin/bash

for subNum in {01..42}
do

echo "Start with subject $subNum"

find /home/kcheung3/sanlab/socialContext/bids_data/derivatives/fmriprep/sub-"$subNum"/func/ -type f -name '*regressors.tsv' -exec cp '{}' /home/kcheung3/sanlab/socialContext/fMRIPrep/qc/output/ ';'


done
