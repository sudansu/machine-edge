import numpy as np
from fastdtw import fastdtw

class FastDynamicTimeWarping:
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
        x = np.array(s1)
        y = np.array(s2)
        distance, _ = fastdtw(x, y)

        return distance

if __name__ == '__main__':
    fdtw = FastDynamicTimeWarping()
    x = [1.1,1.4,2.0]
    y = [2.2, 3.4,6.8]
    dist = fdtw.distance(x,y)
    print(dist)