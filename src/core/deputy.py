import numpy as np
# from sklearn.cluster import AgglomerativeClustering

from common import utils
from dist.dtw import DynamicTimeWarping

class RepresentativeSelection:
    """
    Given a list of source, to cluster them into K clusters, and inside each
    cluster find the most representative source

    Attributes
    ----------
      _srcs: list(list(float))
        internal representation of a list of sources (normalized)
      _dtw: DynamicTimeWarping
        tool for computing dtw
      _clustering: AgglomerativeClustering
        instance of clustering model
      _dists: list(list(float))
        internal buffer for mdistanc eatrix
      _labels: list(int)
        internal buffer for clustering labels
    """

    def __init__(self):
        self._dtw = DynamicTimeWarping()
        self._clustering = AgglomerativeClustering(linkage='complete',
                           n_clusters=num_cluster, affinity="precomputed")

    def fit(self, srcs):
        """
        Set sources to cluster

        Parameters
        ----------
          srcs: list(list(double))
            sources to cluster
        """
        self._srcs = []
        for src in srcs:
          self._srcs.append(utils.get_source_norm(src))

    def cluster(self, num_cluster):
        """
        Cluster into a specified number of clusters

        Parameters
        ----------
          num_cluster: int
            numer of required clusters

        Returns
        -------
          list(int)
            cluster label of each source with value in between [0, k)
        """
        self._dists = self.__cal_dist_matrix()
        self._labels = self._clustering.fit_predict(self._dists)
        return self._labels.copy()

    def find_representative(self, cluster_id):
        """
        Find representative in a cluster

        Parameters
        ----------
          cluster_id: int
            id of cluster to work on

        Returns
        -------
          int
            index of the representative source
        """
        cluster = []
        for i in range(len(self._labels)):
            if self._labels[i] == cluster_id:
                cluster.append(i)
        return self.__cal_representative(cluster)

    def __cal_dist_matrix(self):
        """
        Calculate distance matrix
        """
        dists = np.empty([len(self._srcs), len(self.srcs)])
        for i in range(len(dists)):
            dist[i][i] = 0.0
            for j in range(i+1, len(dists)):
                dists[i][j] = dists[j][i] = self._dtw.distance(self._srcs[i], self._srcs[j])
        return dists

    def __cal_representative(self, cluster):
        """
        Calculate representative
        """
        opt = 1e99
        mark = None
        for s1 in cluster:
            max_dist = 0
            for s2 in cluster:
                max_dist = max(max_dist, self._dist[s1][s2])
            if opt > max_dist:
                opt = max_dist
                mark = s1
        return mark
