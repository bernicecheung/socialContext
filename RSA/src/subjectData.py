from mvpa2.suite import *
import os
import pandas as pd

class subjectData:
    """ This class loads and organizes both behavioral data (rating RDMs computed by pairwise differences)
    and neural data (in a form of fmri_dataset in mvpa2)
    """

    def __init__(self, rootDir, ID, wholebrain):
        """
        Below are the required input.

        :param rootDir: The directory where all the data, masks and codes in.
        :param ID: Subject ID, which starts with 1
        :param run: "P" run number, which starts with 1
        :param hemisphere: "L" indicates left hemisphere mask; "R" indicates right hemisphere mask
        """


        # check the directory input and make sure the format is correct

        if not os.path.exists(rootDir):
            print ('ERROR: %s does not exist!' % rootDir)  # if this is for python 3, it needs a ()
        if not rootDir.endswith('/'):
            rootDir = ''.join([rootDir, '/'])

        # set the root directory
        self.rootDir = rootDir

        # set the subject ID
        self.ID = ID

        # set the run number
        #self.run1 = subjectData.run(1)

        # set the directory for the condition file
        self.conDir = os.path.join(rootDir, "MVPA_prep", "FSL_level1", "scripts", "condition.txt")
        
        
        # set the directory for hemisphere brain mask
        if wholebrain == 'Y':
            self.maskDir = os.path.join(self.rootDir, "brainMask","MNI152_T1_2mm_brain_mask.nii.gz")
        
    
    def importCondition(self):

        """
        This function is for importing the corresponding condition information to a dataframe
        :return: a 4*4 dataframe that contains relavent condition information for each run
        """

        # import the condition file as a dataframe
        conFile = pd.read_csv(self.conDir, sep=" ", header=None)
        conFile.columns = ["subjectID", "runNum", "condition"]

        # extract the corresponding condition information for the current subject
        subCon = conFile[conFile["subjectID"] == self.ID].copy().reset_index(drop=True)
        
        # add a column specifying if the context appears for the first time
        subCon["order"] = [1, 1, 1, 1]
        
        # loop through each row to see if the same context apprears again
        school = 0
        friend = 0
        for rowIdx in range(4):
            if subCon["condition"][rowIdx] == "school": 
                school = school + 1
                if school == 2: 
                    subCon["order"][rowIdx] = 2
            else: 
                friend = friend + 1
                if friend == 2: 
                    subCon["order"][rowIdx] = 2
        
        # the output is a dataframe
        return subCon
        #self.condition = subCon
        

    def runData(self):
        
        self.run1 = self.run(self, 1)
        self.run2 = self.run(self, 2)
        self.run3 = self.run(self, 3)
        self.run4 = self.run(self, 4)
  
    
    class run: 
        
        def __init__(self, subject, runNum):
            """
            """
            
            # set the subject data
            self.subject = subject
            
            # set the run number
            self.runNum = runNum
            
            # extract the condition
            self.condition = self.subject.condition["condition"][self.runNum - 1]
            
            # extract the order
            self.order = self.subject.condition["order"][self.runNum - 1]            
            
            # set the directory for betaseries
            self.betaDir = os.path.join(self.subject.rootDir, "MVPA_prep", "FSL_level1", "model", "sub-{n}".format(n="{:02}".format(self.subject.ID)),
                                        "sub-{n}_task-{c}_run-{r}.feat".format(n="{:02}".format(self.subject.ID), c=self.condition, r=self.runNum), "betaseries", "ev1_LSA_.nii.gz")
            
            # set the diredctory for the ratingRDM
            self.ratingDir = os.path.join(self.subject.rootDir, "RSA", "ratingRDM", "sub-{n}_run-{r}_ratingRDM.txt".format(n="{:02}".format(self.subject.ID), r=self.runNum))
            
            # set the directory for the attribution file
            self.attrDir = os.path.join(self.subject.rootDir, "MVPA_prep", "attributionFiles", "{c}_att.txt".format(c=self.condition))
            
            # convert the attribution file to the corresponding format
            self.att = SampleAttributes(self.attrDir)
    

        def importRatingRDM(self):
            """
            This function is for importing the trait similarity matrix for a given valence and putting it into a vector
            :return: A vector of the lower triangle of the similarity matrix
            """
            # load the trait similarity matrix
            ratingRDM= np.loadtxt(self.ratingDir)
    
            # take lower triangle of the trait similarity matrix and flatten it into a vector
            ratingRDM_flat = np.tril(ratingRDM, k=-1).flatten()
    
            # the output is a vector
            return ratingRDM_flat
        

    
        def importNeural(self):
            """
            This funciton is to load and organize the brain activity data in a format recognized by mvpa module.
            It then subsets the data based on valence, and z score them within each chunk
            :return: a fmri dataset for a given valence after z-score the beta within runs
            """
    
            # convert attribution file format
            #self.att = SampleAttributes(self.attrDir)
    
            # load brain activity data
            betaRaw = fmri_dataset(
                                samples=os.path.join(self.betaDir),
                                targets=np.array(self.att.targets),
                                chunks=self.att.chunks)
            
#            betaRaw = fmri_dataset(
#                                samples=os.path.join(self.betaDir),
#                                targets=np.array(self.att.targets),
#                                chunks=self.att.chunks,
#                                mask=os.path.join(self.maskDir))
#    
#            # subset the dataset based on valence
#            if self.valence == "P":
#                brainData_subset = brainData[brainData.targets == 1]
#            else:
#                brainData_subset = brainData[brainData.targets == -1]
#    
            # remove invariant features of the dataset to free some memory
            betaClean = remove_invariant_features(betaRaw)
    
#            # delete the original dataset to free some memory
#            del brainData
    
            # z-score the beta within each run
            zscore(betaClean, dtype='float32')
    
            # return the neural dataset of a given valence
            return betaClean










