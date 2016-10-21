import pandas as pd
import redis, codecs

class DataSource:
    def __init__(self):
        self._db = redis.StrictRedis()
        # get all options
        self._options = map(codecs.decode, self._db.smembers('daily_sect'))
        self._options = list(sorted(self._options))
        # get all possible timestamps
        df = pd.DataFrame(self._db.zrange('daily_zset', 0, -1, withscores=True))
        self._ts = df[0]
        self._ts.index = pd.Series(pd.to_datetime(df[1], unit='s')) + pd.Timedelta('8 hours')

    def Options(self):
        return self._options

    def GetDataFrame(self, option):
        if (option not in self._options):
            return None
        flds = ['close']
        cols = ['{}:{}'.format(option, _) for _ in flds]
        data = [self._db.hmget(_, cols) for _ in self._ts]
        df = pd.DataFrame(data, columns=flds, index=self._ts.index).dropna().applymap(float)
        return df

