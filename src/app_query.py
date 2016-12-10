import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay
import sys
import os
from source import redis_io
from core import query

from math import pi
from bokeh.io import curdoc, set_curdoc
from bokeh.models import (
    ColumnDataSource, Plot, Circle, Range1d, FactorRange,
    LinearAxis, CategoricalAxis, HoverTool, Text, SingleIntervalTicker,
    CategoricalTicker, CustomJS, BoxSelectTool, HoverTool
)
from bokeh.palettes import Spectral4
from bokeh.resources import INLINE
from bokeh.models.widgets import MultiSelect, Dropdown, Button, Slider, CheckboxGroup, DateRangeSlider, TextInput, Select, Tabs, Panel
from bokeh.layouts import gridplot, row, column, widgetbox, layout
from bokeh.plotting import figure
from bokeh.document import Document
import numpy as np
import talib
from talib.abstract import *
from talib import MA_Type

def Reset():
    global selected
    for _ in _multi_select.value:
        datasource[_].data['color'] = ['black'] * length
        datasource_inc[_].data['color'] = ['#D5E1DD']*length
        datasource_dec[_].data['color'] = ['#F2583E']*length
        datasource_dec[_].data['line_color'] = ['black']*length
        datasource_inc[_].data['line_color'] = ['black']*length
    _mq.reset()
    selected = [True] * length


def SelectData():
    global selected
    factor = "close"
    #print (_select.value, _lower.value, _higher.value)
    _colors = ['red']*length
    _colors_inc = pd.Series(['#D5E1DD']*length)
    _colors_dec = pd.Series(['#F2583E']*length)
    _l = float(_lower.value)
    _h = float(_higher.value)
    element = _select.value
    selected = _mq.query(element, _l, _h)

    for i in range(0, length):
        if selected[i] == False:
            _colors_inc[i] = 'white'
            _colors_dec[i] = 'white'
            _colors[i] = 'white'

    for _ in _multi_select.value:
        datasource[_].data['color'] = _colors
        inc = pd.Series(datasource[_].data['close']) > pd.Series(datasource[_].data['open'])
        dec = pd.Series(datasource[_].data['close']) < pd.Series(datasource[_].data['open'])
        datasource_inc[_].data['color'] = _colors_inc[inc]
        datasource_inc[_].data['line_color'] = pd.Series(_colors)[inc]
        datasource_dec[_].data['color'] = _colors_dec[dec]
        datasource_dec[_].data['line_color'] = pd.Series(_colors)[dec]

def SelectCandle():
    for _ in _multi_select.value:
        colors_inc = pd.Series(['#D5E1DD']*length)
        colors_dec = pd.Series(['#F2583E']*length)
        df = _data[_]

        output = []
        #print("candlestick:", _, _select_candle.value)
        func = _select_candle.value
        if (func == 'DOJI'):
            output = CDLDOJI(df)
        elif func == '2CROWS':
            output = CDL2CROWS(df)
        elif func == 'HAMMER':
            output = CDLHAMMER(df)

        c = ['red']*length
        i = 0
        for o in output:
            if (o == 0):
                c[i] = 'gray'
                colors_inc[i] = 'white'
                colors_dec[i] = 'gray'
            if (selected[i] == False):
                c[i] = 'white'
                colors_inc[i] = 'white'
                colors_dec[i] = 'white'
            i += 1
        datasource[_].data['color'] = c
        inc = pd.Series(datasource[_].data['close']) > pd.Series(datasource[_].data['open'])
        dec = pd.Series(datasource[_].data['close']) < pd.Series(datasource[_].data['open'])
        datasource_inc[_].data['color'] = colors_inc[inc]
        datasource_inc[_].data['line_color'] = pd.Series(c)[inc]
        datasource_dec[_].data['color'] = colors_dec[dec]
        datasource_dec[_].data['line_color'] = pd.Series(c)[dec]

def PrepareFigures():
    global width
    p = {}
    for _sec in _multi_select.value:
        key=_sec
        df=_data[key]
        colors = np.empty(len(df.index), dtype=object)
        colors.fill('red')

        #width = len(df.index)*20
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
        datasource[key] = ColumnDataSource(dict(i=df.index, high=df.high, low = df.low, close=df.close, open=df.open,
            color=['black']*len(df.index)))
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
    #print("remove: ", _multi_select.value[0], plotToRemove)
    listOfSubLayouts.remove(plotToRemove)
    p = PrepareFigures()
    p_container = column(children=p.values(), name='container')
    listOfSubLayouts.append(p_container)


_rs = redis_io.RedisSource(100)
_data = _rs.all_data_frames_dict()
_sec_list = _rs.options()

_mq = query.MultiSeriesQuery()
_mq.fit(_data)

datasource = {}
datasource_inc = {}
datasource_dec = {}
seg = {}
rect_inc = {}
rect_dec = {}
width = 600
length = len(next(iter(_data.values())))
selected = [True] * length

_multi_select = MultiSelect(
    options=_sec_list,
    value = _sec_list[0:3],
    #sizing_mode = "scale_both"
)

_apply_multi = Button(label='Apply', width=60)
_apply_multi.on_click(ChangeSec)

#TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
TOOLS = ""

p = PrepareFigures()

_select = Select(title="Conditions:", value=_multi_select.value[0], options=_multi_select.value)
_lower = TextInput(title="Range", value = '0.0')
_higher = TextInput(value = '999999999.0')
_apply = Button(label='Apply', width=60)
_apply.on_click(SelectData)
_reset = Button(label='Reset', width=60)
_reset.on_click(Reset)
select_plot = column(_select, widgetbox(_lower, _higher), row(_apply, _reset))

candles = ["DOJI", "2CROWS", "HAMMER"]
_select_candle = Select(title="Candlestick:", value=candles[0], options=candles)
_apply_candle = Button(label='Apply', width=60)
_apply_candle.on_click(SelectCandle)
_reset_candle = Button(label='Reset', width=60)
_reset_candle.on_click(Reset)
candle_plot = column(_select_candle, row(_apply_candle, _reset_candle))

tabs = Tabs(tabs=[Panel(child=select_plot, title="Query"), Panel(child=candle_plot, title="CandleSticks")])
w = column(_multi_select, _apply_multi, tabs)
_p_container = column(children=p.values(), name="container")
_chart = column(_p_container, name="chart")
root=row(w, _chart, name="mainLayout")
curdoc().add_root(root)
