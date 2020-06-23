#!/usr/bin/env python
"""pybetaseries: a module for computing beta-series regression on fMRI data

2/14/2015: TD added "all" as a numrealevs option

12/3/2015: TD added if statement in LSA and LSS to handle 1-d arrays for the confound file (numpy treats them as row vectors)
    
Includes:
pybetaseries: main function
spm_hrf: helper function to generate double-gamma HRF
"""

#from mvpa.misc.fsl.base import *
from mvpa2.misc.fsl.base import *
from mvpa2.datasets.mri import fmri_dataset

import numpy as N
import nibabel
import scipy.stats
from scipy.ndimage import convolve1d
from scipy.sparse import spdiags
from scipy.linalg import toeplitz
from mvpa2.datasets.mri import *
import os, sys
from copy import copy
import argparse




class pybetaseries():
    
    def __init__(self,fsfdir,time_res,name):
        #Sets up dataset wide variables
        
        self.name=name
        
        self.time_res=time_res
        
        if not os.path.exists(fsfdir):
            print 'ERROR: %s does not exist!'%fsfdir
            
        if not fsfdir.endswith('/'):
            fsfdir=''.join([fsfdir,'/'])
        
        self.fsfdir=fsfdir
    
        fsffile=''.join([self.fsfdir,'design.fsf'])
        desmatfile=''.join([self.fsfdir,'design.mat'])
    
        design=read_fsl_design(fsffile)
    
        self.desmat=FslGLMDesign2(desmatfile)
        
        self.nevs=self.desmat.mat.shape[1]
        
        
            
        self.ntp=self.desmat.mat.shape[0]
        
        self.TR=round(design['fmri(tr)'],2)
    
        self.hrf=spm_hrf(self.time_res)

        self.time_up=N.arange(0,self.TR*self.ntp+self.time_res, self.time_res);
        
        self.max_evtime=self.TR*self.ntp - 2;
        self.n_up=len(self.time_up)
        
        
        
        if not os.path.exists(fsfdir+'betaseries'):
            os.mkdir(fsfdir+'betaseries')
    
        # load data
        
        maskimg=''.join([fsfdir,'mask.nii.gz'])
        self.raw_data=fmri_dataset(fsfdir+'filtered_func_data.nii.gz',mask=maskimg)
        voxmeans = N.mean(self.raw_data.samples,axis=0)
        self.data=self.raw_data.samples-voxmeans
        
        self.nvox=self.raw_data.nfeatures
        
        cutoff=design['fmri(paradigm_hp)']/self.TR
        
        
        self.F=get_smoothing_kernel(cutoff, self.ntp)
            
    def LSS(self,whichevs,controlcols,conffile):
        method='LSS'
        
        
        print "Calculating LSS: Ev %s" %(whichevs[0])
        
        if len(controlcols)!=0:
            
            if conffile:
                
                dm_nuisanceevs = N.hstack((N.loadtxt(conffile),self.desmat.mat[:, controlcols]))
                
                if N.ndim(dm_nuisanceevs)==1:
                    dm_nuisanceevs = dm_nuisanceevs.reshape(-1,1)
                    
            else:
                dm_nuisanceevs = self.desmat.mat[:, controlcols]
        else:
            if conffile:
                dm_nuisanceevs = N.loadtxt(conffile)
                
                if N.ndim(dm_nuisanceevs)==1:
                    dm_nuisanceevs = dm_nuisanceevs.reshape(-1,1)
                    
                
            else:
                dm_nuisanceevs=[]
            
            
        ons=FslEV3(self.fsfdir+'custom_timing_files/ev%d.txt'%int(whichevs[0]))
        
        
            
        ntrials=len(ons.onsets)
        beta_maker=N.zeros((ntrials,self.ntp))
        dm_trials=N.zeros((self.ntp,ntrials))
        
        for t in range(ntrials):
            if ons.onsets[t] > self.max_evtime:
                continue
            # build model for each trial
            dm_trial=N.zeros(self.n_up)
            window_ons = [N.where(self.time_up==x)[0][0]
                      for x in self.time_up
                      if ons.onsets[t] <= x < ons.onsets[t] + ons.durations[t]]
            
            dm_trial[window_ons]=1
            dm_trial=N.convolve(dm_trial,self.hrf)[0:int(self.ntp/self.time_res*self.TR):int(self.TR/self.time_res)]
            dm_trials[:,t]=dm_trial
        
        dm_full=N.dot(self.F,dm_trials)
        dm_full=dm_full - N.kron(N.ones((dm_full.shape[0],dm_full.shape[1])),N.mean(dm_full,0))[0:dm_full.shape[0],0:dm_full.shape[1]]
        
        
            
        for p in range(len(dm_full[1,:])):
            target=dm_full[:,p]
            dmsums=N.sum(dm_full,1)-dm_full[:,p]
            if len(dm_nuisanceevs)>0:
                des_loop=N.hstack((target[:,N.newaxis],dmsums[:,N.newaxis],dm_nuisanceevs))
            else:
                des_loop=N.hstack((target[:,N.newaxis],dmsums[:,N.newaxis]))
            beta_maker_loop=N.linalg.pinv(des_loop)
            beta_maker[p,:]=beta_maker_loop[0,:]
                
        # this uses Jeanette's trick of extracting the beta-forming vector for each
        # trial and putting them together, which allows estimation for all trials
        # at once
        
        glm_res_full=N.dot(beta_maker,self.data)
        ni=map2nifti(self.raw_data,data=glm_res_full)
        ni.to_filename(self.fsfdir+'betaseries/ev%d_%s_%s.nii.gz'%(int(whichevs[0]),method,self.name))
            
    def LSA(self,whichevs,controlcols,conffile):
        method='LSA'
        print "Calculating LSA"
        
        if len(controlcols)!=0:
            
            if conffile:
                
                dm_nuisanceevs = N.hstack((N.loadtxt(conffile),self.desmat.mat[:, controlcols]))
                
                if N.ndim(dm_nuisanceevs)==1:
                    dm_nuisanceevs = dm_nuisanceevs.reshape(-1,1)
            else:
                dm_nuisanceevs = self.desmat.mat[:, controlcols]
        else:
            if conffile:
                dm_nuisanceevs = N.loadtxt(conffile)
                
                if N.ndim(dm_nuisanceevs)==1:
                    dm_nuisanceevs = dm_nuisanceevs.reshape(-1,1)
                    
            else:
                dm_nuisanceevs=[]
            
             
        all_onsets=[]
        all_durations=[]
        all_conds=[]  # condition marker
        for e in range(len(whichevs)):
            ev=whichevs[e]
            ons=FslEV3(self.fsfdir+'custom_timing_files/ev%d.txt'%int(ev))       
            all_onsets=N.hstack((all_onsets,ons.onsets))
            all_durations=N.hstack((all_durations,ons.durations))
            all_conds=N.hstack((all_conds,N.ones(len(ons.onsets))*(ev)))
        ntrials=len(all_onsets)
        glm_res_full=N.zeros((self.nvox,ntrials))
        dm_trials=N.zeros((self.ntp,ntrials))
        dm_full=[]
        for t in range(ntrials):
            if all_onsets[t] > self.max_evtime:
                continue
            dm_trial=N.zeros(self.n_up)
            window_ons = [N.where(self.time_up==x)[0][0]
                      for x in self.time_up
                      if all_onsets[t] <= x < all_onsets[t] + all_durations[t]]
            
            dm_trial[window_ons]=1
            dm_trial=N.convolve(dm_trial,self.hrf)[0:int(self.ntp/self.time_res*self.TR):int(self.TR/self.time_res)]
            dm_trials[:,t]=dm_trial
            
        dm_full=N.dot(self.F,dm_trials)
        dm_full=dm_full - N.kron(N.ones((dm_full.shape[0],dm_full.shape[1])),N.mean(dm_full,0))[0:dm_full.shape[0],0:dm_full.shape[1]]
        
        if len(dm_nuisanceevs)>0:
            dm_full=N.hstack((dm_full,dm_nuisanceevs))
        else:
            pass
        
            
        glm_res_full=N.dot(N.linalg.pinv(dm_full),self.data)
        glm_res_full=glm_res_full[0:ntrials,:]
    
        for e in whichevs:
            ni=map2nifti(self.raw_data,data=glm_res_full[N.where(all_conds==(e))[0],:])
            ni.to_filename(self.fsfdir+'betaseries/ev%d_%s_%s.nii.gz'%(int(e),method,self.name))

        
def get_smoothing_kernel(cutoff, ntp):
    sigN2 = (cutoff/(N.sqrt(2.0)))**2.0
    K = toeplitz(1
                 /N.sqrt(2.0*N.pi*sigN2)
                 *N.exp((-1*N.array(range(ntp))**2.0/(2*sigN2))))
    K = spdiags(1./N.sum(K.T, 0).T, 0, ntp, ntp)*K
    H = N.zeros((ntp, ntp)) # Smoothing matrix, s.t. H*y is smooth line
    X = N.hstack((N.ones((ntp, 1)), N.arange(1, ntp+1).T[:, N.newaxis]))
    for  k in range(ntp):
        W = N.diag(K[k, :])
        Hat = N.dot(N.dot(X, N.linalg.pinv(N.dot(W, X))), W)
        H[k, :] = Hat[k, :]

    F = N.eye(ntp) - H
    return F




def spm_hrf(TR,p=[6,16,1,1,6,0,32]):
    """ An implementation of spm_hrf.m from the SPM distribution

    Arguments:

    Required:
    TR: repetition time at which to generate the HRF (in seconds)

    Optional:
    p: list with parameters of the two gamma functions:
                                                         defaults
                                                        (seconds)
       p[0] - delay of response (relative to onset)         6
       p[1] - delay of undershoot (relative to onset)      16
       p[2] - dispersion of response                        1
       p[3] - dispersion of undershoot                      1
       p[4] - ratio of response to undershoot               6
       p[5] - onset (seconds)                               0
       p[6] - length of kernel (seconds)                   32

    """

    p=[float(x) for x in p]

    fMRI_T = 16.0

    TR=float(TR)
    dt  = TR/fMRI_T
    u   = N.arange(p[6]/dt + 1) - p[5]/dt
    hrf=scipy.stats.gamma.pdf(u,p[0]/p[2],scale=1.0/(dt/p[2])) - scipy.stats.gamma.pdf(u,p[1]/p[3],scale=1.0/(dt/p[3]))/p[4]
    good_pts=N.array(range(N.int(p[6]/TR)))*N.int(fMRI_T)
    print p[6]
    print good_pts
    hrf=hrf[list(good_pts)]
    # hrf = hrf([0:(p(7)/RT)]*fMRI_T + 1);
    hrf = hrf/N.sum(hrf);
    return hrf


class FslGLMDesign2(object):
    """Load FSL GLM design matrices from file.
    Be aware that such a desig matrix has its regressors in columns and the
    samples in its rows.
    """
    def __init__(self, source):
        """
        Parameters
        ----------
        source : filename
          Compressed files will be read as well, if their filename ends with
          '.gz'.
        """
        # XXX maybe load from array as well
        self._load_file(source)


    ##REF: Name was automagically refactored
    def _load_file(self, fname):
        """Helper function to load GLM definition from a file.
        """
        # header info
        nwaves = 0
        ntimepoints = 0
        matrix_offset = 0

        # open the file compressed or not
        if fname.endswith('.gz'):
            import gzip
            fh = gzip.open(fname, 'r')
        else:
            fh = open(fname, 'r')

        # read header
        for i, line in enumerate(fh):
            if line.startswith('/NumWaves'):
                nwaves = int(line.split()[1])
            if line.startswith('/NumPoints'):
                ntimepoints = int(line.split()[1])
            if line.startswith('/PPheights'):
                self.ppheights = [float(i) for i in line.split()[1:]]
            if line.startswith('/Matrix'):
                matrix_offset = i + 1

        # done with the header, now revert to NumPy's loadtxt for convenience
        fh.close()
        self.mat = N.loadtxt(fname, skiprows=matrix_offset)

        if len(self.mat.shape) == 1:
            self.mat=self.mat.reshape([self.mat.shape[0],1])

        # checks
        if not self.mat.shape == (ntimepoints, nwaves):
            raise IOError, "Design matrix file '%s' did not contain expected " \
                           "matrix size (expected %s, got %s)" \
                           % (fname, str((ntimepoints, nwaves)), self.mat.shape)


if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument('--fsldir',dest='fsldir',default='',help='Path to Target FSL Directory')
    parser.add_argument('--whichevs', dest='whichevs',type=int, nargs='*',help='List of EVs to Compute Beta Series for. Number corresponds to real EV number in FEAT (starting with 1).')
    parser.add_argument('--conffile',dest='conffile',default=None,help='Path to Confound File (optional)')
    parser.add_argument('--controlcols',dest='controlcols',default=N.array([]),nargs='*',type=int,help='Columns in original FEAT design matrix to control for (starting at 1; optional)')
    parser.add_argument('--timeres',dest='timeres',type=float,default=0.001, help='Time resolution for convolution.')
    parser.add_argument('--name',dest='name',default="",type=str, help='Optional Name Extension.')
    parser.add_argument('-LSA',dest='LSA',action='store_true',
            default=False,help='Include tag to compute LSA.')
    parser.add_argument('-LSS',dest='LSS',action='store_true',
            default=False,help='Include tag to compute LSS.')
    
    
    args = parser.parse_args()
        
    if len(args.controlcols)>0:
        args.controlcols=[i-1 for i in args.controlcols]
    
    #If nothing in conffile
    if args.conffile:
        cc=N.loadtxt(args.conffile)
        if len(cc) == 0:
            args.conffile=None
        
    pybeta=pybetaseries(args.fsldir,args.timeres,args.name)
    if args.LSS:
        all_control=N.hstack((args.whichevs,N.array(args.controlcols)))
        
        if len(args.whichevs)>1:
            
            print "NOTE: MORE THAN ONE EV DETECTED; Using LSS-N approach; Design matrix column for EVs assumed to = real EV# (Don't use with temporal derivatives in model)."
            
            for ev in args.whichevs:
                
                other_ev_control = N.array([i-1 for i in args.whichevs if i != ev])
                
                full_conf=N.hstack((args.controlcols,other_ev_control))
                full_conf=full_conf.astype(int)
                print full_conf
                
                pybeta.LSS([ev],full_conf,args.conffile)
            
        else:
            pybeta.LSS([args.whichevs[0]],N.array(args.controlcols),args.conffile)

        
            
            
    if args.LSA:
        pybeta.LSA(args.whichevs,N.array(args.controlcols),args.conffile)
        
