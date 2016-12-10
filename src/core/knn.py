import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

from common import utils
from dist.dtw import DynamicTimeWarping

class KnnGaussianPrediction:
    """
    Given a source and a choosen sub-interval, to find kNN of that change
    pattern, and predict future plots using Gaussian processing

    Attributes
    ----------
      _src: list(float)
        internal representation of current source (change rate/norm)
      _dtw: DynamicTimeWarping
        tool for computing dtw
      _gp: GaussianProcessingRegressor
        instance of gaussian predictor
    """

    def __init__(self):
        self._dtw = DynamicTimeWarping()
        self._gp = GaussianProcessRegressor(n_restarts_optimizer=3)

    def fit(self, src):
        """
        Set source to predict

        Parameters
        ----------
          src: list(double)
            source to predict
        """
        self._src = utils.get_source_change_rate(src)

    def get_knn(self, start, end, k):
        """
        Given an interval, find k neighbors

        Parameters
        ----------
          start: int
            start position
          end: int
            end position
          k: int
            number of required neighbors

        Returns
        -------
          list([float, int])
            k tuples in format [distance, position]
        """
        scores = self.__cal_distance(start, end)
        top_k = self.__select_top_k(scores, k, end-start)
        return top_k

    def predict(self, start, end, top_k, look_ahead):
        """
        Predict using Gaussian processing based on top k neighbors

        Parameters
        ----------
          start: int
            start position
          end: int
            end position
          top_k: list([float, int])
            top k neighbors
          look_ahead: int
            number of points to predict

        Returns
        -------
          list(float), list(float)
            predicted values, standart errors
        """
        print ("Start Predict...")
        k = len(top_k)
        l = end-start
        X = [] # Input samples(shape : n_samples * n_features)
        Y = [] # Expected label (shape: n_samples * look_ahead)
        for i in range(k):
            offset = top_k[i][1] + l
            x = []
            for j in range(top_k[i][1], offset):
                x.append(self._src[j])
            X.append(x)
            y = []
            for j in range(look_ahead):
                y.append(self._src[offset + j])
            Y.append(y)
        np_X = np.array(X)
        np_Y = np.array(Y)
        print("np_X = " + str(np_X))
        print("np_Y = " + str(np_Y))
        # Fit to data using Maximum Likelihood Estimation of the parameters
        self._gp.fit(np_X, np_Y)
        input_segment = [self._src[start:end]]
        np_segment = np.array(input_segment)
        # print("np_segment: " + str(np_segment))
        y_preds,stds = self._gp.predict(np_segment,return_std=True)
        # print ("y_pred: " + str(y_preds))
        # print("std: " + str(stds))
        return y_preds[0], stds[0]

    def __cal_distance(self, start, end):
        """
        Calculate all possible distances against an interval

        Parameters
        ----------
          start: int
            start position
          end: int
            end position

        Returns
        -------
          list([float, int])
            list of tuples in format [distance, position]
        """
        l = end - start
        ret = []
        matrix = np.empty([l+1, l+1])
        for i in range(0, len(self._src) - l + 1):
            score = self._dtw.distance(self._src[start:end], self._src[i:i+l])
            ret.append([score, i])
        return ret

    def __select_top_k(self, scores, k, min_dist):
        """
        Select k smallest distance

        Parameters
        ----------
          scores: list([float, int])
            sequence of tuples in format [distance, position]
          k: int
            number of selected points
          min_dist: int
            minimum position difference between any selected points
        """
        scores = sorted(scores)
        ret = []
        for score in scores:
            v = score[1]
            ok = True
            for old in ret:
                if (abs(v-old[1]) < min_dist):
                    ok = False
                    break
            if ok:
                ret.append(score)
                if len(ret) > k:
                    break
        # Remove the first element, which is the same as the input segment
        return ret[1:]
