#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 21:18:59 2020

@author: BerniceCheung
"""

import nilearn
from nilearn import image

# load the original wholebrain mask used by fMRIPrep
oriMask = image.load_img('/Users/BerniceCheung/Documents/Bernice/socialContext/brainMask/mni_icbm152_nlin_asym_09c_nifti/mni_icbm152_nlin_asym_09c/mni_icbm152_t1_tal_nlin_asym_09c_mask.nii')

# load the beta serie file as the target
target = image.load_img('/Users/BerniceCheung/Documents/Bernice/socialContext/MVPA_prep/FSL_level1/model/sub-01/sub-01_task-friend_run-1.feat/betaseries/ev1_LSA_.nii.gz')

# exact one volumn from the target
targetVolumn = image.index_img(target, 1)

# resample the mask to the target space
resampledMask = image.resample_to_img(oriMask,targetVolumn)

# write the resampled mask
resampleedMask.to_filename('/Users/BerniceCheung/Documents/Bernice/socialContext/brainMask/mni_icbm152_nlin_asym_09c_resampled.nii')