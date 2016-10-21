import numpy as np

class KnnPrediction:
    def SetSource(self, source):
        self._source = source
        self._rate = [1]
        for i in range(1, len(source)):
            self._rate.append(source[i]/source[i-1]);

    def GetTopKnn(self, start, end, K):
        scores = self.__CalDtwDist(start, end)
        top_k = self.__SelectTopK(scores, K, end-start)
        print(top_k)
        return top_k

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
                if len(ret) >= K:
                    break
        return ret
