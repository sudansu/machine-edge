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
        self._model = hmm.GaussianHMM(n_components=2, covariance_type="spherical",n_iter=200)

    def fit(self, src):
        """
        Set source to prdict

        Parameters:
        -----------
          src: list(double)
            source to predict
        """
        src_change_rate = utils.get_source_change_rate(src) * 100.0
        self._src = np.reshape(src_change_rate, (-1,1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._model.fit(self._src)
        print("Transmat_", self._model.transmat_)
        print("means_", self._model.means_)
        print("covars_", self._model.covars_)

    def predict(self):
        """
        Predict probability of in turbulance state

        Returns:
        --------
          list(double)
            list of probability that each point is in turbulance state
        """

        flatten_convars = self._model.covars_.flatten()
        if(flatten_convars[0] > flatten_convars[1]):
            turbulance_state = 0
        else:
            turbulance_state = 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Z = self._model.predict_proba(self._src)
        return [p[turbulance_state] for p in Z]

if __name__ == '__main__':
    r = RegimeShiftIdentifier()
    r.fit([5,6,7,8,9])
    print(r.predict())