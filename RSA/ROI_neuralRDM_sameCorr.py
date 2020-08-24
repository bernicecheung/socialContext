'''
This script is used to calculate the correlation between the neural RDMs of runs in the same context.
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
    parser.add_argument('--context', dest='context', default='', type=str,
                        choices=["friend", "school"], help='Choose the context for the same contect correlation between neural RDMs')

    # generate inputs
    inputs = parser.parse_args()

    # set the root directory for the project
    root_dir = inputs.rootDir

    # set the context for the project
    context = inputs.context

    # load condition file
    conDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'condition.txt'), sep=" ",
                        header=None)

    # rename the columns
    conDf.columns = ["subjectID", "runNum", "condition"]

    # load stimuli file
    stimDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'stimuliDf.csv'))

    # load the trait list
    traitDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'traitList.csv'))

    # extract the trait as the reference order
    ref_order = traitDf['Trait'].tolist()

    # load the whole brain parcellation mask
    mask = Brain_Data(os.path.join(root_dir, 'brainMask', 'Neurosynth Parcellation', 'Neurosynth Parcellation_2.nii.gz'))

    # get a list of ROIs
    mask_x = expand_mask(mask)

    print("Complete loading input files")

    # create a BIDS object

    layout = BIDSLayout(os.path.join(root_dir,'bids_data'), derivatives=True)

    # return a list of subject IDs
    sub_list = layout.get(target='subject', return_type='id')

    print("Complete generating a BIDS object")

    # initiate a dictionary for same context correlation
    sameContextCorr = {}

    # loop through each subject
    for subID in sub_list:

        print(f'Start with subject {subID}')

        # convert subID format to integer
        sub = int(subID)

        # extract the corresponding condition information for the current subject
        subCon = conDf[conDf["subjectID"] == sub].copy().reset_index(drop=True)

        # look up the corresponding run number for the current context
        context_runNum = subCon.loc[subCon["condition"] == context, 'runNum'].values

        # initiate a dictionary to store neuralRDM for the current context
        context_neuralRDM = {}

        print('Complete initialization')

        # loop through both runs in the current context
        for order, run in enumerate(context_runNum, start=1):

            print(f'Start with order-{order}, run-{run}')

            # load the beta data
            beta_dir = os.path.join(root_dir, 'MVPA_prep', 'FSL_level1', 'model', f'sub-{subID}',
                                    f'sub-{subID}_task-{context}_run-{run}.feat', 'betaseries', 'ev1_LSA_.nii.gz')
            beta = Brain_Data(beta_dir)

            print('Complete loading beta')

            # extract trait presentation order
            idx = stimDf.loc[(stimDf['subID'] == sub) & (stimDf['runNum'] == run)].index
            trait_order = stimDf['currentTrait'].iloc[idx].tolist()

            # generate the index to match the reference order
            match_idx = [trait_order.index(i) for i in ref_order]

            # rearrange the order of the beta series to match the reference trait order
            beta_reorder = beta[match_idx]

            print('Complete reordering beta')

            # initiate a list neuralRDM in each ROIs
            ROI_neuralRDM = []

            # loop through each ROI and generate neuralRDM
            print('Start looping through each ROI')

            for ROI_idx, m in enumerate(mask_x):
                # correlation distance ranges from 0-2
                # and subtracting this value from 1 yields similarity scores in the form of pearson correlations
                similarityMatrix = 1 - beta_reorder.apply_mask(m).distance(metric='correlation')

                # add trait names as the labels
                similarityMatrix.labels = ref_order

                # append the outcomes to the list
                ROI_neuralRDM.append(similarityMatrix)

                # write the correlation distance in a form of square matrix
                similarityMatrix_dir = os.path.join(root_dir,'RSA', 'neuralRDM', f'sub-{subID}',
                                                    f'sub-{subID}_{context}_order-{order}_ROI-{ROI_idx}-neuralRDM.csv')

                similarityMatrix.write(similarityMatrix_dir, method='square')

            print('Complete generating neuralRDM for each ROI')
            # store all neuralRDMs with the key of the current run
            context_neuralRDM[order] = ROI_neuralRDM

        print('Complete generating neuralRDM for both runs')

        # loop through each ROI and calculate similarity between two neuralRDM from the same context
        # (spearman correlation with 5000 permutation)
        context_corr = [x.similarity(y) for x, y in zip(context_neuralRDM[1], context_neuralRDM[2])]

        # extract the correlation coefficient
        context_corrCoe = [x['correlation'] for x in context_corr]

        # store the same context correlation to the dictionary
        sameContextCorr[sub] = context_corrCoe

        print(f'Complete calculating the similarity for same context neural RDM for subject-{subID}')

    print('Complete calculating similarity for all subjects')

    # convert the list to a dataframe, which each column represents a ROI and each row represents a subject
    sameContextCorrDf = pd.DataFrame(sameContextCorr).T

    # write the dataframe
    output_dir = os.path.join(root_dir,'RSA', 'outputs', f'neuralRDM_sameCorr_ROI_{context}.csv')
    sameContextCorrDf.to_csv('output_dir')

