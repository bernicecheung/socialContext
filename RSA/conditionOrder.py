import os
import numpy as np
import pandas as pd

# set the project directory
root_dir = "/Users/BerniceCheung/Documents/ResearchProject/socialContext"

# import the condition file
conDf = pd.read_csv(os.path.join(root_dir, 'RSA', 'inputs', 'condition.txt'), sep=" ",
                        header=None)

# rename the columns
conDf.columns = ["subjectID", "runNum", "condition"]

# create a column for context orders
conDf["order"] = np.ones(conDf.shape[0])

# extract a list of subject IDs
subIDs = conDf.subjectID.unique()

# loop through each subject
for sub in subIDs:

    # initialize the order
    school = 0
    friend = 0

    # extract the row index corresponding to the present subject
    rowIdx = conDf[conDf["subjectID"] == sub].index

    # loop through each run
    for idx in rowIdx: 

        # count the number of presence for each context and record the order
        if conDf["condition"][idx] == "school": 
            school = school + 1
            if school == 2: 
                conDf["order"][idx] = 2
        else: 
            friend = friend + 1
            if friend == 2: 
                conDf["order"][idx] = 2

# write the modified condition file
conDf.to_csv(os.path.join(root_dir, 'RSA', 'inputs', 'condition_order.txt'), header=None, index=None, sep=' ', float_format='%.f')

