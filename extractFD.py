#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 06:52:54 2019

@author: BerniceCheung
"""

import pandas as pd
from glob import glob

subIDs = ["%.2d" % i for i in range(1, 43)]
subIDs.remove("05")
runIDs = range(1, 5)
outlierDf = pd.DataFrame(columns=['subID', 'runNum', 'FD_mean', 'FD_max', 'FD_sd', 0.3, 0.4, 0.5, 0.6, 0.9], index=range(164))
threshold = [0.3, 0.4, 0.5, 0.6, 0.9]

rowIdx = 0
for subNum in subIDs:
    
    print "start with subject {}".format(subNum)

    for runNum in runIDs:
        print "start with run {}".format(runNum)
        
       
        runFileDir = '/home/kcheung3/sanlab/socialContext/bids_data/derivatives/fmriprep/sub-{}/func/*run-{}_desc-confounds_regressors.tsv'.format(subNum,runNum)
    
        runFile = glob(runFileDir)
        
        print runFile
        
        outlierDf.at[rowIdx, 'subID'] = subNum
        outlierDf.at[rowIdx, 'runNum'] = runNum
    
        if runFile:
            fullDf = pd.read_csv(runFile[0], sep='\t')
            fd = fullDf['framewise_displacement']
            outlierDf.at[rowIdx, 'FD_mean'] = fd.mean()
            outlierDf.at[rowIdx, 'FD_max'] = fd.max()
            outlierDf.at[rowIdx, 'FD_sd'] = fd.std()
            
            for T in threshold:
                outlier = fd[fd > T]
                outlierDf.at[rowIdx, T] = len(outlier)
           
        rowIdx = rowIdx + 1    

outlierDf.to_csv('/home/kcheung3/sanlab/socialContext/fMRIPrep/qc/thresholdTestOutput.csv', index=False)
