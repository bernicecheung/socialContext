import argparse
from subjectData import subjectData
from neuroCorrelation import neuroCorrelation
from mvpa2.suite import *
import copy
import types
#from pprocess import *

if __name__ == "__main__":
    # define import arguments
    parser = argparse.ArgumentParser(description='RSA dataset parameters')
    parser.add_argument('--rootDir', dest='rootDir', type=str, default='', help='Path to the root directory of all inputs')
    parser.add_argument('--ID', dest='ID', type=int, default='', help='Subject ID (starts with 1)')
    parser.add_argument('--context', dest='context', type=str,
                        choices=["friend", "school"], default='',
                        help='Choose the context for the RSA analysis')
    parser.add_argument('--wholebrain', dest='wholebrain', type=str,
                        choices=["Y", "N",], default='Y', help='Y: wholebrain searchlight, N: conduct RSA within ROIs')
    parser.add_argument('--rad', dest='rad', type=int,
                        default='', help='Set the radius for search light')

    # generate inputs
    inputs = parser.parse_args()

    print ("Start with subject{n}".format(n=inputs.ID))

    # create an object from the subjectData class
    subject = subjectData(inputs.rootDir, inputs.ID, inputs.wholebrain)
    
    # extract the condition information for all 4 runs
    subject.condition = subject.importCondition()
    
    # extract the run number corresponding to the fisrt presence of the present context
    runNum = subject.condition.loc[(subject.condition['condition'] == inputs.context) & (subject.condition['order'] == 1),'runNum'].values[0]
    
    # create an object from the run class for each context
    run = subject.run(subject, runNum)
    
    # load the rating RDM for the current run
    ratingRDM = run.importRatingRDM()
    
    # load the beta series (neural data)
    beta = run.importNeural()
    
    print("Complete data loading")
    
    # create an object from the neuroCorrelation class
    matrixCorr = neuroCorrelation(ratingRDM)
    
    # set the radius based on the input
    rad = inputs.rad
    
    # Fisher's z-transformation for correlation coefficient
    FisherTransform = FxMapper('features', lambda r: 0.5 * np.log((1 + r) / (1 - r)))
    
    # create the search light
    #sl = sphere_searchlight(matrixCorr.correlate, rad, postproc=FisherTransform, nproc = 1, nblocks = 5, results_backend = 'hdf5')
    sl = sphere_searchlight(matrixCorr.correlate, rad, postproc=FisherTransform, nproc = 1, nblocks = 5, results_backend = 'hdf5')
    
    print ("Complete search light set-up")

    # apply the search light function to the neural data
    sl_output = sl(beta)

    print ("Search light completed")

    # transform the search light output to an image data
    sl_image = map2nifti(data=sl_output, dataset=beta)
    
    # save the output
    outputDir = os.path.join(inputs.rootDir, "RSA", "searchLightResult", "sub-{n}".format(n="{:02}".format(inputs.ID)),
                             "sub-{n}_sl_wholebrain_{c}.nii.gz".format(n="{:02}".format(inputs.ID), c=inputs.context))
    sl_image.to_filename(outputDir)

    print ("Complete with subject{n}".format(n=inputs.ID))