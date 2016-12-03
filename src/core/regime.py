import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from hmmlearn import hmm
import warnings

from common import utils

class RegimeShiftIdentifier:
    """
    Given a source, to indicate the probability that a point is in turbulance
    state

    Attributes
    ----------
      _src: list(float)
        internal representation of current source (change rate/norm)
      _model: GaussianHMM
        instance of GaussitanHMM model
    """

    def __init__(self):
        self.model = hmm.GaussianHMM(n_components=2, covariance_type="spherical",n_iter=200)

    def fit(self, src):
        """
        Set source to prdict

        Parameters:
        -----------
          src: list(double)
            source to predict
        """
        self._src = utils.get_source_change_rate(src)

    def predict(self):
        """
        Predict probability of in turbulance state

        Returns:
        --------
          list(double)
            list of probability that each point is in turbulance state
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(np.array(self._rate))
        print("Transmat_", self.model.transmat_)
        print("means_", self.model.means_)
        print("covars_", self.model.covars_)
        flatten_convars = self.model.covars_.flatten()
        if(flatten_convars[0] > flatten_convars[1]):
            turbulance_state = 0
        else:
            turbulance_state = 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Z = self.model.predict_proba(np.array(self._rate))
        return [p[turbulance_state] for p in Z]
