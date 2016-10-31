import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

class KnnPrediction:
    def SetSource(self, source):
        self._source = source
        self._rate = [1]
        for i in range(1, len(source)):
            self._rate.append(source[i]/source[i-1]);

    def GetTopKnn(self, start, end, K):
        scores = self.__CalDtwDist(start, end)
        top_k = self.__SelectTopK(scores, K, end-start)
#        print(top_k)
        return top_k

    def GP_Predict(self, start,end,top_k):
        print ("Start GP_Predict: ")
        k = len(top_k)
        l = end-start
        X = [] # Input samples(shape : n_samples * n_features)
        Y = [] # Expected label (shape: n_samples * look_ahead)
        for i in range(0,k):
            offset = top_k[i][1] + l
            x = []

            for j in range(top_k[i][1], offset):
                x.append(self._rate[j])

            X.append(x)

            look_ahead = 3
            y = []
            for j in range(look_ahead):
                y.append(self._rate[offset + j])
            Y.append(y)

        np_X = np.array(X)
        np_y = np.array(Y)
        print("np_X = ")
        print(np_X)
        print("np_y = ")
        print(np_y)
        print()

        gp = GaussianProcessRegressor(n_restarts_optimizer=3)

# Fit to data using Maximum Likelihood Estimation of the parameters
        gp.fit(np_X, np_y)

        input_segment = [self._rate[start:end]]
        np_segment = np.array(input_segment)
        print("np_segment: ")
        print (np_segment)
        y_preds,stds = gp.predict(np_segment,return_std=True  )
        print ("y_pred: ")
        print(y_preds)
        print("std: ")
        print(stds)
        return y_preds, stds

    def Predict(self, start, end, top_k):
        k = len(top_k)
        l = end-start
        min_v = []
        max_v = []
        sum_v = []
        for i in range(0, k):
            offset = top_k[i][1] + l
            for j in range(0, k):
                if (i == 0):
                    min_v.append(self._rate[offset+j])
                    max_v.append(self._rate[offset+j])
                    sum_v.append(self._rate[offset+j])
                else:
                    min_v[j] = min(min_v[j], self._rate[offset+j])
                    max_v[j] = max(max_v[j], self._rate[offset+j])
                    sum_v[j] = sum_v[j] + self._rate[offset+j]
        avg_v = [x/k for x in sum_v]
        return avg_v, min_v, max_v

    def __CalDtwDist(self, start, end):
        l = end - start
        ret = []
        matrix = np.empty([l+1, l+1])
        for i in range(0, len(self._source) - l + 1):
            score = self.__Dtw(matrix, self._rate[start:end], self._rate[i:i+l])
            ret.append([score, i])
        return ret

    def __Dtw(self, f, s1, s2):
        w = 0.0
        l = len(s1)
        for i in range(0, l+1):
            f[0][i] = 1e99
            f[i][0] = 1e99
        f[0][0] = 0
        for i in range(1, l+1):
            for j in range(1, l+1):
                f[i][j] = abs(s1[i-1]-s2[j-1]) + min(f[i-1][j-1], f[i][j-1], f[i-1][j])
        return f[l][l]

    def __SelectTopK(self, scores, K, min_dist):
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
                if len(ret) >= K + 1:
                    break
        #Remove the first element, which is the same as the input segment
        return ret[1:]
