'''
This script is used to calculate the correlation between the neural RDMs of runs across different contexts.
'''

import os
from glob import glob
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
    parser.add_argument('--friendOrder', dest='friendOrder', default='', type=str,
                        choices=["1", "2"], help='Choose the run order for the friend context')
    parser.add_argument('--schoolOrder', dest='schoolOrder', default='', type=str,
                        choices=["1", "2"], help='Choose the run order for the school context')

    # generate inputs
    inputs = parser.parse_args()

    # set the root directory for the project
    root_dir = inputs.rootDir

    # set the run order for each context
    friendOrder = inputs.friendOrder
    schoolOrder = inputs.schoolOrder

    # load condition file
    conDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'condition_order.txt'), sep=" ",
                        header=None)
    
    # rename the columns
    conDf.columns = ["subjectID", "runNum", "condition", "order"]

    # load the trait list
    traitDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'traitList.csv'))

    # extract the trait as the reference order
    ref_order = traitDf['Trait'].tolist()
    
    print("Complete loading input files")

    # create a BIDS object

    layout = BIDSLayout(os.path.join(root_dir,'bids_data'), derivatives=True)

    # return a list of subject IDs
    sub_list = layout.get(target='subject', return_type='id')
    
    print("Complete generating a BIDS object")

    # initiate a dictionary for the different context correlation
    diffContextCorr = {}

    # loop through each subject
    for subID in sub_list:

        print(f'Start with subject {subID}')

        # convert subID format to integer
        sub = int(subID)

        # extract the corresponding condition information for the current subject
        subCon = conDf[conDf["subjectID"] == sub].copy().reset_index(drop=True)

        # extract neuralRDMs directory
        sub_neuralRDM_dir = os.path.join(root_dir,'RSA', 'neuralRDM', f'sub-{subID}')
        
        print('Complete initialization')

        # grab all file names correspoding to the friend run, and re-order them based on ROI number
        friend_namePatten = f'{sub_neuralRDM_dir}/*_friend_order-{friendOrder}_*'
        friend_RDM_fileNames = sorted(glob(friend_namePatten, recursive=True), key=lambda name: int(name[108:-14]))

        # import csv files for each ROI into a list
        friend_neuralCSV = [pd.read_csv(f) for f in friend_RDM_fileNames]

        # convert each csv into an adjacency objective
        friend_neuralRDM = [Adjacency(f, matrix_type='distance', labels= ref_order) for f in friend_neuralCSV]
        
        print('Complete loading the friend neural RDM')
        
        # grab all file names correspoding to the school run, and re-order them based on ROI number
        school_namePatten = f'{sub_neuralRDM_dir}/*_school_order-{schoolOrder}_*'
        school_RDM_fileNames = sorted(glob(school_namePatten, recursive=True), key=lambda name: int(name[108:-14]))
        
        # import csv files for each ROI into a list
        school_neuralCSV = [pd.read_csv(f) for f in school_RDM_fileNames]
        
        # convert each csv into an adjacency objective
        school_neuralRDM = [Adjacency(f, matrix_type='distance', labels= ref_order) for f in school_neuralCSV]

        print('Complete loading the school neural RDM')

        # loop through each ROI and calculate similarity between two neuralRDM from both contexts
        # (spearman correlation with 5000 permutation)
        context_corr = [x.similarity(y) for x, y in zip(friend_neuralRDM, school_neuralRDM)]

        # extract the correlation coefficient
        context_corrCoe = [x['correlation'] for x in context_corr]

        # score the different context correlatoin to the dictionary
        diffContextCorr[sub] = context_corrCoe

        print(f'Complete calculating the similarity for diff context neural RDM for subject-{subID}')
    
    print('Complete calculating similarity for all subjects')
    
    # convert the list to a dataframe, which each column represents a ROI and each row represents a subject
    diffContextCorrDf = pd.DataFrame(diffContextCorr).T

    # write the dataframe. The number after F represents the order of the friend context and the number after S represents the order of the school context
    output_dir = os.path.join(root_dir,'RSA', 'outputs', f'neuralRDM_diffCorr_ROI_F{friendOrder}S{schoolOrder}.csv')
    diffContextCorrDf.to_csv(output_dir)

