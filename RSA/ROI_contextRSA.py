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
    parser.add_argument('--context', dest='context', default='', type=str,
                        choices=["friend", "school"], help='Choose the context for the RSA between neural and rating')
    parser.add_argument('--contextOrder', dest='contextOrder', default='', type=str,
                        choices=["1", "2"], help='Choose the run order for the present context')

    # generate inputs
    inputs = parser.parse_args()

    # set the root directory for the project
    root_dir = inputs.rootDir

    # set the run order for each context
    context = inputs.context
    contextOrder = inputs.contextOrder

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

    # initiate a dictionary for the RSA of the present context
    contextRSA = {}

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

        # grab all file names correspoding to the present run, and re-order them based on ROI number
        namePatten = f'{sub_neuralRDM_dir}/*_{context}_order-{contextOrder}_*'

        # count the number of string before the ROI number and after the ROI number
        rootLen = len(root_dir)
        preLen = len(f'/RSA/neuralRDM/sub-01/sub-01_{context}_order-{contextOrder}_ROI-')
        postLen = len("-neuralRDM.csv")

        NeuralRDM_fileNames = sorted(glob(namePatten, recursive=True), key=lambda name: int(name[(rootLen + preLen):-postLen]))

        # import csv files for each ROI into a list
        neuralCSV = [pd.read_csv(f) for f in NeuralRDM_fileNames]

        # convert each csv into an adjacency objective
        neuralRDM = [Adjacency(f, matrix_type='distance', labels= ref_order) for f in neuralCSV]
        
        print('Complete loading the neuralRDM')

        # set rating RDM directory for the present context
        ratingRDM_dir = os.path.join(root_dir,'RSA', 'inputs', 'ratingRDM_sameOrder', f'sub-{subID}_{context}_ratingRDM.csv')

        # import the ratingRDM as CSV and convert it to an adjacency object
        ratingCSV = pd.read_csv(ratingRDM_dir)
        ratingRDM = Adjacency(ratingCSV, matrix_type='distance', labels= ref_order)

        print('Complete loading the ratingRDM')

        # loop through each ROI and calculate similarity between neuralRDM and ratingRDM (spearman correlation with 5000 permutation)
        RDM_corr = [x.similarity(ratingRDM) for x in neuralRDM]

        # extract the correlation coefficient
        RDM_corrCoe = [x['correlation'] for x in RDM_corr]

        # store the RSA for the present study into the dictionary (key is the subID)
        contextRSA[sub] = RDM_corrCoe

        print(f'Complete calculating the similarity for diff context neural RDM for subject-{subID}')

    print('Complete calculating similarity for all subjects')

    # convert the list to a dataframe, which each column represents a ROI and each row represents a subject
    contextRSADf = pd.DataFrame(contextRSA).T

    # write the RSA output for each ROI in the present context
    output_dir = os.path.join(root_dir,'RSA', 'outputs', f'contextRSA_{context}.csv')
    contextRSADf.to_csv(output_dir)