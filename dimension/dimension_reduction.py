import numpy as np
from sklearn.cluster import AgglomerativeClustering

class Dim_Red:

    def SetOptions(self, option):
        self._option = option

    def SetSource(self, source):
        self._source = source
        self._rate = self.SetNormRate(source)

    def SetRate(self, source):

        rate = np.empty([len(source), len(source[0])])        

        # self._option = option

        for i in range(len(rate)):
            rate[i][0] = 1
            for j in range(1,len(rate[i])):
                rate[i][j] = source[i][j] / source[i][j-1]
        return rate

    def SetNormRate(self, source):
        rate = np.empty([len(source), len(source[0])])        
        for i in range(len(rate)):
            min_s = min(source[i])
            max_s = max(source[i])

            for j in range(1, len(rate[i])):
                rate[i][j] = (source[i][j] - min_s) / (max_s - min_s)

        return rate

    def __Dtw(self, f, s1, s2):
        # print("s1",s1)
        # print("s2",s2)
        # input()
        w = 0.0
        l = len(s1)
        # print ("L Len: ", l)
        for i in range(0, l+1):
            f[0][i] = 1e99
            f[i][0] = 1e99
        f[0][0] = 0
        for i in range(1, l+1):
            for j in range(1, l+1):
                f[i][j] = abs(s1[i-1]-s2[j-1]) + min(f[i-1][j-1], f[i][j-1], f[i-1][j])
        return f[l][l]


    def GetDistMatrix(self):
        length = len(self._rate[0]) + 1
        f = np.empty([length, length])        
        # print("1st dim: ", len(f))
        # print("2nd dim: ", len(f[0]))
        dists = np.empty([len(self._option), len(self._option)])        

        for i in range(len(self._option)):

            for j in range(i+1, len(self._option)):
                # print("i = ",i, " rate i: ", self._rate[i])
                # print("j", j, " rate j: ", self._rate[j])
                # input()
                dists[i][j] = dists[j][i] = self.__Dtw(f, self._rate[i], self._rate[j])

        return dists

        # for i in range(1, len(source)):
        #     self._rate.append(source[i]/source[i-1]);

    def GetClusters(self,dists, num_cluster):

        clustering = AgglomerativeClustering(linkage='complete', n_clusters=num_cluster,affinity="precomputed")

        result = clustering.fit_predict(dists)

        # print(result)
        return result

    def GetRepre(self, dists, labels,num_cluster):
        '''
        return a dict: repre -> a list of other options in cluster
        '''
        result = dict() 
        for i in range(num_cluster):
            cluster = []
            for j in range(len(labels)):
                if labels[j] == i:
                    cluster.append(j)
            repre = self.__GetRepre(dists, cluster)
            cluster.remove(repre)

            result[repre] = cluster
        return result

    def __GetRepre(self, dists, cluster):

        dist_min = 1e99
        mark_min = 0

        # print("cluster: ", cluster)

        for c in cluster:
            max_dis = 0
            for cc in cluster:
                max_dis = max(max_dis, dists[c][cc])
            if dist_min > max_dis:
                dist_min = max_dis
                mark_min = c
        # print("dist_min: ", dist_min)
        # print("mark_min: ", mark_min)
        return mark_min





