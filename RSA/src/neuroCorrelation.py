import numpy as np
from scipy import stats
class neuroCorrelation:
    """
    This class is for the correlation between trait similarity matrix and neural correlation matrix
    """
    # include the flattened trait similarity matrix into the class
    def __init__(self, traitMatrix):
        """
        :param traitMatrix: this is a vector of the lower triangle of trait similarity matrix of a given valence.
        """
        self.traitMatrix = traitMatrix

    def correlate(self, brainData):
        """
        generate a function which generate the coefficient of a person correlation between the neural matrix and the trait similarity matrix
        :param brainData: this is a fmri_dataset of a given valence after z-scoring within runs
        :return: the correlation coefficient between neural correlation matrix and trait similarity matrix of a given valence
        """
        # generate a similarity matrix across each pair of samples
        neuro_sim = np.corrcoef(brainData.samples)

        # take lower triangle of the neuro similarity matrix and flatten
        neuro_sim_flat = np.tril(neuro_sim, k=-1).flatten()

        # generage a mask matrix of 1
        ones_matrix = np.ones(np.shape(neuro_sim))

        # take lower triangle of the ones matrix and flatten to generate a mask
        onesflat = np.tril(ones_matrix, k=-1).flatten()

        # calculate the correlation between neuro similarity matrix and trait similarity matrix, and apply the mask to take the lower triangle
        corr_output = stats.pearsonr(neuro_sim_flat[onesflat != 0], self.traitMatrix[onesflat != 0])

        # only return the correlation coefficient, but not the p-value
        return corr_output[0]