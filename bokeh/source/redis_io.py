import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay
import redis

class RedisSource:
    """
    Data source loaded from redis.

    Attributes:
        _data: list of DataFrames loaded from redis
        _sec_list: list of options
        _db: the redis database
    """

    def __init__(self, day=10000):
        self._data = {}
        self._db = redis.StrictRedis()

        # load securities list
        _raw_list = list(self._db.smembers('daily_sect')) #db
        self._sec_list = list(map(codecs.decode, _raw_list))

        _grp_raw_dict = self._db.hgetall('sect_grp') #db
        self._sec_grp_df = pd.DataFrame(_raw_list, columns = ['sec'])
        self._sec_grp_df['grp'] = self._sec_grp_df['sec'].map(_grp_raw_dict)
        self._sec_grp_df = self._sec_grp_df.applymap(codecs.decode).sort_values('grp')
        #print(self._sec_grp_df)

        #day = 10000
        # prepare 'time since' list dropdown
        _start = pd.to_datetime('today').tz_localize('UTC').tz_convert('Asia/Singapore') - day * BDay()
        #_end = pd.to_datetime('now').tz_localize('UTC').tz_convert('Asia/Singapore')
        #_dt_rng = pd.date_range(start=_start,end=_end,freq='B',tz='Asia/Singapore')
        #_dt_rng_strf = list(_dt_rng.strftime('%Y-%b-%d'))
        #_dt_rng_dict = dict(zip(_dt_rng_strf, _dt_rng))

        # retrieve data based on 'time since' and 'securities list'
        _s = int(_start.timestamp())
        _zset = self._db.zrangebyscore('daily_zset', _s, math.inf, withscores=True) #db
        _zset_df = pd.DataFrame(_zset)

        _time_index = _zset_df[1].map(functools.partial(pd.to_datetime, unit='s'))
        _time_index.name='time'
        _elements = ['close', 'open', 'high', 'low', 'vol30']
        _sec_data = {}
        for _sec in self._sec_list:
            _cols = [_sec + ':' + _ele for _ele in _elements]
            _sec_data[_sec]=[self._db.hmget(_t[0],_cols) for _t in _zset] #db
            self._data[_sec] = pd.DataFrame(_sec_data[_sec], columns = pd.Series(_elements,name='sec'), index=_time_index)
            self._data[_sec].index = self._data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore')
            #_data[_sec].index = _data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
            self._data[_sec] = self._data[_sec].fillna(method='ffill').fillna(method='bfill').applymap(float)

    def options(self):
        """
        Returns
        -------
        list(string)
          all options
        """
        return self._sec_list

    def groups(self):
        """
        Returns
        -------
        DataFrame('sec', 'grp')
          sec to grp map
        """
        return self._sec_grp_df

    def data_frame(self, option, start_point=None, end_point=None):
        """
        Get a data frame within a time interval

        Parameters
        ----------
        option : string
          the security name, e.g., eur_curny
        start_point: int
          optional, start position of the dataframe
        end_point: int
          optional, end position of the dataframe

        Returns
        -------
        DataFrame
          the required DataFrame
        """
        return self._data[option][start_point : end_point]

    def all_data_frames(self, start_point=None, end_point=None):
        """
        Get all data frames within a time interval

        Parameters
        ----------
        start_point: int
          optional, start position of the dataframe
        end_point: int
          optional, end position of the dataframe

        Returns
        -------
        list(DataFrame)
          a list of DataFrames
        """

        ret = []
        for _ in self._sec_list:
          ret.append(self._data[_][start_point : end_point])
        return ret

    def all_data_frames_dict(self, start_point=None, end_point=None):
        """
        Get all data frames within a time interval

        Parameters
        ----------
        start_point: int
          optional, start position of the dataframe
        end_point: int
          optional, end position of the dataframe

        Returns
        -------
        list(DataFrame)
          a dict of DataFrames
        """
        ret = {}
        for _ in self._sec_list:
            ret[_] = self._data[_][start_point:end_point]
        return ret

if __name__ == "__main__":
    rs = RedisSource(365)
    options = rs.options()
    print("options are: ", options)
    print()
    groups = rs.groups()
    print(groups)
    print()
    df = rs.data_frame(options[0], None, 10)
    print("data_frame is: ", df)
    print()
    df = rs.all_data_frames(None, 10)
    print("all_data_frames are: ", df)