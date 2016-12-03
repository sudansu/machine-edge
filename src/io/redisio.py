import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay
import redis

class RedisSource:
	def __init__(self, day=10000):
		self._data = {}
		self._db = redis.StrictRedis()

		# load securities list
		_raw_list = list(self._db.smembers('daily_sect')) #db
		self.sec_list = list(map(codecs.decode, _raw_list))

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
		_elements = ['close', 'open', 'high', 'low']
		_sec_data = {}
		for _sec in self.sec_list:
		    _cols = [_sec + ':' + _ele for _ele in _elements]
		    _sec_data[_sec]=[self._db.hmget(_t[0],_cols) for _t in _zset] #db
		    self._data[_sec] = pd.DataFrame(_sec_data[_sec], columns = pd.Series(_elements,name='sec'), index=_time_index)
		    self._data[_sec].index = self._data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore')
		    #_data[_sec].index = _data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
		    self._data[_sec] = self._data[_sec].fillna(method='ffill').fillna(method='bfill').applymap(float)

	def options(self):
		return self.sec_list

	def data_frame(self, option, start_point=None, end_point=None):
		"""
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
		for _ in self.sec_list:
			ret.append(self._data[_][start_point : end_point])
		return ret


def main():
	rs = RedisSource(365)
	options = rs.options()
	print("options are: ", options)
	print()
	df = rs.data_frame(options[0], None, 10)
	print("data_frame is: ", df)
	print()
	df = rs.all_data_frames(None, 10)
	print("all_data_frames are: ", df)

if __name__ == "__main__":
    main()

