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
       # print ("self._ts")
       # print (self._ts)
        self._ts.index = pd.Series(pd.to_datetime(df[1], unit='s')) + pd.Timedelta('8 hours')
        #print ("self._tx.index")
        #print (self._ts.index)

    def Options(self):
        return self._options

    def GetDataFrame(self, option):
        if (option not in self._options):
            return None
        flds = ['close']
        cols = ['{}:{}'.format(option, _) for _ in flds]
        # print ("cols: ")
        # print(cols)
        data = [self._db.hmget(_, cols) for _ in self._ts]
        # print ("data: ")
        # print(data)
        df = pd.DataFrame(data, columns=flds, index=self._ts.index).dropna().applymap(float)
        # print ("df: ")
        # print (df)
        return df

