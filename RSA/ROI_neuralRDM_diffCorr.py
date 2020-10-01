'''
This script is used to calculate the correlation between the neural RDMs of runs across different contexts.
'''

import os
import glob
import numpy as np
import pandas as pd
import argparse
import seaborn as sns
from nltools.data import Brain_Data, Adjacency
from nltools.mask import expand_mask, roi_to_brain
from nltools.stats import fdr, threshold, fisher_r_to_z, one_sample_permutation
from sklearn.metrics import pairwise_distances
from nilearn.plotting import plot_glass_brain, plot_stat_map, view_img_on_surf, view_img
from bids import BIDSLayout, BIDSValidator

if __name__ == "__main__":
    # define import arguments
    parser = argparse.ArgumentParser(description='Social Context ROI parameters')
    parser.add_argument('--rootDir', dest='rootDir', default='', help='Path to the root directory of BIDS data')
    parser.add_argument('--order', dest='order', default='', type=str,
                        choices=[1, 2], help='Choose the context for the same contect correlation between neural RDMs')

    # generate inputs
    inputs = parser.parse_args()

    # set the root directory for the project
    root_dir = inputs.rootDir

    # load condition file
    conDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'condition_order.txt'), sep=" ",
                        header=None)
    
    # rename the columns
    conDf.columns = ["subjectID", "runNum", "condition", "order"]


    