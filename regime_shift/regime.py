import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from hmmlearn import hmm
import warnings

class RegimeIdentifier(object):
    """docstring for RegimeIdentifier"""
    def __init__(self):
        self.model = hmm.GaussianHMM(n_components=2, covariance_type="spherical",n_iter=200)

    def SetSource(self, source):
        self._source = source
        self._rate = [[0.0]]
        for i in range(1, len(source)):
            self._rate.append([(source[i]/source[i-1] - 1.0) * 100]);

    def predict(self):
        '''
            Use hmm model to identify regime, totally two hidden states, 0 and 1.

            Emission Distribution for both states: Normal Distributions

            State 0: stable state, the hidden state with low variance
            State 1: turbulance state, the hidden state with high variance

            return a list of bool
                set to true if in turbulance state
            
        '''
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(np.array(self._rate))
        # print("Transmat_", self.model.transmat_)
        # print("means_", self.model.means_)
        # print("covars_", self.model.covars_)

        flatten_convars = self.model.covars_.flatten()
        if(flatten_convars[0] > flatten_convars[1]):
            turbulance_state = 0
        else:
            turbulance_state = 1

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Z = self.model.predict(np.array(self._rate))
        # print ("Turbulance State: ", turbulance_state)
        is_turbulent = [state == turbulance_state for state in list(Z.flatten())]
        
        # zero_count = 0
        # one_count = 0
        # for i,e in enumerate(list(Z.flatten())):
        #     if e == 0:
        #         zero_count += 1
        #     else:
        #         #print (i)
        #         one_count += 1

        # print("Len: ", len(self._rate))
        # print ("Zero Count: ", zero_count)
        # print ("one_count: ", one_count)

        return is_turbulent