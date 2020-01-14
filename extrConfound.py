#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 02:11:20 2019

@author: BerniceCheung
"""

import pandas as pd
from glob import glob
import argparse
import numpy as np

#
# define input
parser = argparse.ArgumentParser(description='provide all the subject IDs and run numbers')
parser.add_argument('-maxSubID', default=None, type=int,
                    help='this will generate a list of subject IDs from 01 to this number. The input must be an integer.')
parser.add_argument('-maxRunNum', default=None, type=int,
                    help='this will generate a list of run numbers from 1 to this number. The input must be an integer.')
parser.add_argument('-BIDS_dir', default=None, type=str,
                    help='this is the absolute directory of the BIDS folder. The input must ends with a /')
parser.add_argument('-out_dir', default=None, type=str,
                    help='this is the absolute output directory. The input must ends with a /')
parser.add_argument('-fd_threshold', default=None, type=str,
                    help='this is the threshold for framewise displacement /')
parser.add_argument('--removeID', default=None, type=str, nargs='+',
                    help='this is the IDs to be removed from the list of subject IDs. The input must be double digit')
parser.add_argument('--minSubID', default=1, type=int,
                    help='this is the subject ID to start with. The input must be an integer. The default is 1')
# store inputs
my_input = parser.parse_args()

# transform fd threshold to numeric
fd_threshold = float(my_input.fd_threshold)

# generate a list of subject IDs and run numbers
subIDs = ["%.2d" % i for i in range(my_input.minSubID, my_input.maxSubID + 1)]

# remove IDs from the removeID input
if my_input.removeID is not None:
    removeList = my_input.removeID
    subIDs = [ID for ID in subIDs if ID not in removeList]

# generate a list of run number
runNums = range(1, my_input.maxRunNum + 1)

for subNum in subIDs:
    print("start with subject {}".format(subNum))

    for runNum in runNums:
        print("start with run {}".format(runNum))

        # locate confound file
        runFileDir = my_input.BIDS_dir + 'derivatives/fmriprep/sub-{}/func/*run-{}_desc-confounds_regressors.tsv'.format(
            subNum, runNum)

        runFile = glob(runFileDir)

        if runFile:
            # extract the confound file as a dataframe
            fullDf = pd.read_csv(runFile[0], sep='\t')

            # subset the dataframe with motion parameters and fd columns
            select_cos = ['trans_x', 'trans_x_derivative1', 'trans_y', 'trans_y_derivative1', 'trans_z',
                           'trans_z_derivative1', 'rot_x', 'rot_x_derivative1', 'rot_y', 'rot_y_derivative1', 'rot_z',
                           'rot_z_derivative1', 'framewise_displacement']
            selectDf = fullDf.filter(items=select_cos)

            # replace NaN with 0s
            selectDf = selectDf.fillna(0)

            # loop through each row
            motionOutlier_count = 0
            row_count = len(selectDf.index)

            for idx, fd in enumerate(selectDf.framewise_displacement):

                if fd > fd_threshold:
                    col_content = [0] * row_count
                    col_content[idx] = 1
                    selectDf['motion_outlier%.2d' % motionOutlier_count] = col_content


            # delete the fd column
            finalDf = selectDf.drop(columns=['framewise_displacement'])

            # write relevant columns into a csv file
            selectDf.to_csv(my_input.out_dir + 'sub-{}_run-{}_confound.txt'.format(subNum, runNum), header=None, index=None, sep=' ')
