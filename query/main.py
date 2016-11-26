import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay
import redis

from math import pi
from bokeh.sampledata.stocks import MSFT
from bokeh.io import push_notebook, show, output_notebook, curdoc, set_curdoc, push, reset_output, push_session
from bokeh.models import (
    ColumnDataSource, Plot, Circle, Range1d, FactorRange,
    LinearAxis, CategoricalAxis, HoverTool, Text, SingleIntervalTicker,
    CategoricalTicker, CustomJS, BoxSelectTool, HoverTool
)
from bokeh.palettes import Spectral4
from bokeh.resources import INLINE
from bokeh.models.widgets import MultiSelect, Dropdown, Button, Slider, CheckboxGroup, DateRangeSlider, TextInput, Select
from bokeh.layouts import gridplot, row, column, widgetbox, layout
from bokeh.plotting import figure
from bokeh.document import Document
import numpy as np
#import talib
#from talib.abstract import *
#from talib import MA_Type


def Reset():
    global colors
    length = len(colors)
    for _ in _multi_select.value:
        datasource[_].data['color'] = ['black'] * length
        datasource_inc[_].data['color'] = ['#D5E1DD']*length
        datasource_dec[_].data['color'] = ['#F2583E']*length
        datasource_dec[_].data['line_color'] = ['black']*length
        datasource_inc[_].data['line_color'] = ['black']*length
    colors = ['red'] * length

def SelectData():
    global colors
    factor = "close"
    print (_select.value, _lower.value, _higher.value)
    length = len(colors)
    selected = [False]*length
    _colors = ['white']*length
    _colors_inc = pd.Series(['#D5E1DD']*length)
    _colors_dec = pd.Series(['#F2583E']*length)
    _l = float(_lower.value)
    _h = float(_higher.value)
    element = _select.value
    i=0
    for _ in _data[element][factor]:
        if _ >= _l and _ <= _h and colors[i] == 'red':
            _colors[i] = 'red'
            selected[i] = True
        else:
            _colors_inc[i] = 'white'
            _colors_dec[i] = 'white'
        i = i + 1

    colors = _colors
    for _ in _multi_select.value:
        datasource[_].data['color'] = _colors
        inc = pd.Series(datasource[_].data['close']) > pd.Series(datasource[_].data['open'])
        dec = pd.Series(datasource[_].data['close']) < pd.Series(datasource[_].data['open'])
        datasource_inc[_].data['color'] = _colors_inc[inc]
        datasource_inc[_].data['line_color'] = pd.Series(_colors)[inc]
        datasource_dec[_].data['color'] = _colors_dec[dec]
        datasource_dec[_].data['line_color'] = pd.Series(_colors)[dec]


def PrepareFigures():
    global colors
    global width
    p = {}
    for _sec in _multi_select.value:
        key=_sec
        df=_data[key]
        colors = np.empty(len(df.index), dtype=object)
        colors.fill('red')

        width = 800 #len(df.index)*20
        p[key] = figure(x_axis_type="datetime", tools=TOOLS, title = key+" candlestick chart", plot_width=width, plot_height=200, name=key)
        p[key].xaxis.major_label_orientation = pi/4
        p[key].grid.grid_line_alpha=0.3

        mids = (df.open + df.close)/2
        spans = abs(df.close-df.open)
        inc = df.close > df.open
        dec = df.open > df.close
        w = 12*60*60*1000 # half day in ms

        inc_len = len(mids[inc])
        dec_len = len(mids[dec])
        datasource[key] = ColumnDataSource(dict(i=df.index, high=df.high, low = df.low, close=df.close, open=df.open, color=['black']*len(df.index)))
        datasource_inc[key] = ColumnDataSource(dict(mids=mids[inc], spans=spans[inc], i=df.index[inc],
            color=["#D5E1DD"]*inc_len, line_color=['black']*inc_len))
        datasource_dec[key] = ColumnDataSource(dict(mids=mids[dec], spans=spans[dec], i=df.index[dec],
            color=["#F2583E"]*dec_len, line_color=['black']*dec_len))
        #seg[key] = p[key].segment(df.index, df.high, df.index, df.low, color=colors)
        seg[key] = p[key].segment('i', 'high', 'i', 'low', color='color', source = datasource[key])
        #rect_inc[key] = p[key].rect(df.index[inc], mids[inc], w, spans[inc], fill_color="#D5E1DD", line_color="black")
        #rect_dec[key] = p[key].rect(df.index[dec], mids[dec], w, spans[dec], fill_color="#F2583E", line_color="black")
        rect_inc[key] = p[key].rect('i', 'mids', w, 'spans', source = datasource_inc[key], fill_color="color", line_color="line_color")
        rect_dec[key] = p[key].rect('i', 'mids', w, 'spans', source = datasource_dec[key], fill_color="color", line_color="line_color")
    return p


def ChangeSec():
    _select.options = _multi_select.value
    _select.value = _multi_select.value[0]
    rootLayout = curdoc().get_model_by_name('chart')
    listOfSubLayouts = rootLayout.children
    plotToRemove = curdoc().get_model_by_name('container')
    print("remove: ", _multi_select.value[0], plotToRemove)
    listOfSubLayouts.remove(plotToRemove)
    p = PrepareFigures()
    p_container = column(children=p.values(), name='container')
    listOfSubLayouts.append(p_container)



db = redis.StrictRedis()

# load securities list
_raw_list = list(db.smembers('daily_sect')) #db
_sec_list = list(map(codecs.decode, _raw_list))
#_sec_list = ['jpy_curncy', 'ty1_comdty', 'jb1_comdty']

# prepare 'time since' list dropdown
_start = pd.to_datetime('today').tz_localize('UTC').tz_convert('Asia/Singapore') - 100 * BDay()
#_end = pd.to_datetime('now').tz_localize('UTC').tz_convert('Asia/Singapore')
#_dt_rng = pd.date_range(start=_start,end=_end,freq='B',tz='Asia/Singapore')
#_dt_rng_strf = list(_dt_rng.strftime('%Y-%b-%d'))

# retrieve data based on 'time since' and 'securities list'
_s = int(_start.timestamp())
_zset = db.zrangebyscore('daily_zset',_s,math.inf, withscores=True) #db
_zset_df = pd.DataFrame(_zset)

_time_index = _zset_df[1].map(functools.partial(pd.to_datetime, unit='s'))
_time_index.name='time'
_elements = ['close', 'open', 'high', 'low']
#_cols = [_+':'+_ele for _ele in _elements for _ in _sec_list]
_sec_data = {}
_data = {}
for _sec in _sec_list:
    _cols = [_sec + ':' + _ele for _ele in _elements]
    _sec_data[_sec]=[db.hmget(_t[0],_cols) for _t in _zset] #db
    _data[_sec] = pd.DataFrame(_sec_data[_sec], columns = pd.Series(_elements,name='sec'), index=_time_index)
    _data[_sec].index = _data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore')
    #_data[_sec].index = _data[_sec].index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
    _data[_sec] = _data[_sec].fillna(method='ffill').fillna(method='bfill').applymap(float)


_multi_select = MultiSelect(
    options=_sec_list,
    value = [_sec_list[0],_sec_list[1]],
    #sizing_mode = "scale_both"
)

_apply_multi = Button(label='Apply', width=60)
_apply_multi.on_click(ChangeSec)

#TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
TOOLS = ""

datasource = {}
datasource_inc = {}
datasource_dec = {}
seg = {}
rect_inc = {}
rect_dec = {}
colors = []
width = 600
p = PrepareFigures()


#output = CDLDOJI(df)

_select = Select(title="Conditions:", value=_multi_select.value[0], options=_multi_select.value)
_lower = TextInput(title="Range", value = '0.0')
_higher = TextInput(value = '100000.0')
_apply = Button(label='Apply', width=60)
_apply.on_click(SelectData)
_reset = Button(label='Reset', width=60)
_reset.on_click(Reset)
w = column(_multi_select, _apply_multi, _select, widgetbox(_lower, _higher), row(_apply, _reset))
_p_container = column(children=p.values(), name="container")
_chart = column(_p_container, name="chart")
root=row(w, _chart, name="mainLayout")
curdoc().add_root(root)
