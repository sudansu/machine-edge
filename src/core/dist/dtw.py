import numpy as np

class DynamicTimeWarping:
    """
    Attributes
    ----------
      _f: 2d matrix(float)
        buffer for computing distance
    """

    def __init__(self):
        self._f = np.empty([1, 1])

    def distance(self, s1, s2):
        """
        Get DTW distance

        Args
        ----
          s1: list(float)
            first source list
          s2: list(float)
            second source list

        Returns
        -------
        float
          computed DTW distance
        """
        assert len(s1) == len(s2)
        l = len(s1)
        if len(self._f) < l+1:
            self._f = np.empty([l+1, l+1])
        for i in range(l+1):
            self._f[i][0] = 1e99
            self._f[0][i] = 1e99
        self._f[0][0] = 0
        for i in range(1, l+1):
            for j in range(1, l+1):
                self._f[i][j] = abs(s1[i-1]-s2[j-1]) +  min(self._f[i-1][j-1], self._f[i][j-1], self._f[i-1][j])
        return self._f[l][l]
