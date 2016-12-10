import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay


class MultiSeriesQuery:
    """
    Query based on multiple series.

    Attributes:
        _selected: the current times that satisfy the conditions, a list of [True, False]
        _source: all the DataFrames loaded from redis (either a dict or a list)
        _length: total size of time points
    """
    def __init__(self):
        self._selected = []

    def reset(self):
        """
        reset the condition, i.e., change the selected list to all True
        """
        self._selected = [True] * self._length

    def fit(self, source):
        """
        put the data source

        Parameters
        ----------
        source : list/dict of DataFrame
            list/dict of DataFrame
        """
        self._source = source
        self._length = len(next(iter(self._source.values())))
        self.reset()

    def query(self, source_id, min_val, max_val):
        """
        query the DataFrame identified by source_id, on top of the current selected stats

        Parameters
        ----------
        source_id : int/string
            int/string based on the _source type
        min_val: float
          minimum value
        max_val: float
          maximum value

        Returns
        -------
        DataFrame
            the query results stored as a list of True/False
        """
        factor = "close"
        i = 0
        for _ in self._source[source_id][factor]:
            if _ < min_val or _ > max_val:
                self._selected[i] = False
            i = i + 1    
        return self._selected