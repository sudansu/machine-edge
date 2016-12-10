import codecs, math, functools
import pandas as pd
from pandas.tseries.offsets import BDay
import redis

from bokeh.io import push_notebook, show, output_notebook, curdoc
from bokeh.models import (
    ColumnDataSource, Plot, Circle, Range1d, FactorRange,
    LinearAxis, CategoricalAxis, HoverTool, Text, SingleIntervalTicker,
    CategoricalTicker, CustomJS, BoxSelectTool
)
from bokeh.palettes import Spectral4
from bokeh.resources import INLINE
from bokeh.models.widgets import MultiSelect, Dropdown, Button, Slider
from bokeh.layouts import gridplot, row, column, widgetbox, layout
import sys
import os
from source import redis_io


def animate():
    '''
    callback function for play button
    '''
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)


def ChangeTimeSince(new=None):
    '''
    callback function for time since Select
    slice the data according to the start time point
    '''
    global _data, _data_vol
    _dropdown.value=new
    _dropdown.label=new

    # get the partition of the _data since new
    _data = _data.T
    _data.index = _data.index.map(functools.partial(pd.to_datetime))
    _data = _data[new:]
    _data.index = _data.index.strftime('%Y-%b-%d')
    _data = _data.T

    # get the partition of the _data_vol since new
    _data_vol = _data_vol.T
    _data_vol.index = _data_vol.index.map(functools.partial(pd.to_datetime))
    _data_vol = _data_vol[new:]
    _data_vol.index = _data_vol.index.strftime('%Y-%b-%d')
    _data_vol = _data_vol.T

    _text_source.data['time'] = [_data.columns[_slider.value]]


def ChangeSelection():
    '''
    callback function for apply button for the MultiSelection of options 
    update the securities/options set displayed in the figure
    '''
    global _data, _data_vol
    global _max

    _sec_data = {}
    _vol_data = {}
    for _ in _select.value:
        _sec_data[_] = _rs.data_frame(_)['close']
        _vol_data[_] = _rs.data_frame(_)['vol30']

    _data = pd.DataFrame(_sec_data)
    _data = (_data / _data.iloc[0] - 1) * 100
    _data.index = _data.index.strftime('%Y-%b-%d')
    _data = _data.T

    _data_vol = pd.DataFrame(_vol_data)
    _data_vol.index = _data_vol.index.strftime('%Y-%b-%d')
    _data_vol = _data_vol.T

    #update the xrange and yrange
    _x = list(_data.index)
    plot.x_range.factors = _x

    #update the _max value
    _max = _data.shape[1] - 1

    #update the circle
    i=_slider.value
    vol_size_fator = 50/_data_vol.values.max()
    _circle_renderer.data_source.data['x']=list(_data.index)
    _circle_renderer.data_source.data['y']=list(_data.iloc[:,i])
    _circle_renderer.data_source.data['size']=list(_data_vol.iloc[:,i]*vol_size_fator)
    _circle_renderer.data_source.data['color']=[_color_map[_i] for _i in list(_data.index)]

    #update time
    _text_source.data['time'] = [_data.columns[_slider.value]]


def slider_update(attrname, old, new):
    '''
    callback function for the slider on change action 
    update the data according to the selected time point
    '''
    i=_slider.value
    _circle_renderer.data_source.data['y']=list(_data.iloc[:,i])
    _circle_renderer.data_source.data['size']=list(_data_vol.iloc[:,i]*vol_size_fator)
    _text_renderer.data_source.data = ColumnDataSource({'time': [_data.columns[i]]}).data


def animate_update():
    '''
    update the slider value by 1
    called by the animate function periodically
    '''
    value = _slider.value + 1
    if value > _max:
        value = _slider.end
    _slider.value = value


# prepare 'time since' list dropdown
days = 365
_rs = redis_io.RedisSource(days)

# prepare securities multiple select
# load securities grouping
_sec_grp_df = _rs.groups()
_options = list(_sec_grp_df['sec'])
_select = MultiSelect(
    options=_options,
    value = _options[0:10],
    #value = [_options[10],],
    #sizing_mode = "scale_both"
    #width=200
)
# the multi_select apply button
_select_button = Button(label='Apply', width=60)
_select_button.on_click(ChangeSelection)


# load the close and vol30 data
_sec_data = {}
_vol_data = {}
for _ in _select.value:
    _sec_data[_] = _rs.data_frame(_)['close']
    _vol_data[_] = _rs.data_frame(_)['vol30']

# close dataframe
_data = pd.DataFrame(_sec_data)
_data.index = _data.index.strftime('%Y-%b-%d')
_data = (_data / _data.iloc[0] - 1) * 100
_data = _data.T

# vol30 dataframe
_data_vol = pd.DataFrame(_vol_data)
_data_vol.index = _data_vol.index.strftime('%Y-%b-%d')
_data_vol = _data_vol.T

# assign colors
_color_dict = dict(zip(_sec_grp_df['grp'].unique(),Spectral4))
_sec_grp_df['color'] = _sec_grp_df['grp'].map(_color_dict)
_color_map = dict(zip(list(_sec_grp_df['sec']),list(_sec_grp_df['color'])))


# prepare dropdown options for time since
_start = pd.to_datetime('now').tz_localize('UTC').tz_convert('Asia/Singapore') - days * BDay()
_end = pd.to_datetime('now').tz_localize('UTC').tz_convert('Asia/Singapore')
_dt_rng = pd.date_range(start=_start,end=_end,freq='B',tz='Asia/Singapore')
_dt_rng_strf = list(_dt_rng.strftime('%Y-%b-%d'))
_dt_rng_dict = dict(zip(_dt_rng_strf, _dt_rng))
_menu = list(zip(_dt_rng_strf, _dt_rng_strf))
_dropdown = Dropdown(
    #options=_opt,
    menu=_menu,
    default_value=_dt_rng_strf[0],
    label=_dt_rng_strf[0],
    #width=200
)
_dropdown.on_click(ChangeTimeSince)


# prepare plot
_x = list(_data.index)
_x_rng = FactorRange(factors = _x)

_margin = 2 #percent
_y_min = _data.values.min()
_y_max = _data.values.max()
_y_rng = Range1d(_y_min-_margin, _y_max+_margin)
plot = Plot(
    x_range=_x_rng,
    y_range=_y_rng,
    plot_width=750,
    plot_height=400,
    outline_line_color=None,
    toolbar_location=None,
    min_border=20)

AXIS_FORMATS = dict(
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
    major_label_text_font_size="10pt",
    major_label_text_font_style="normal",
    axis_label_text_font_size="10pt",

    axis_line_color='#AAAAAA',
    major_tick_line_color='#AAAAAA',
    major_label_text_color='#666666',

    major_tick_line_cap="round",
    axis_line_cap="round",
    axis_line_width=1,
    major_tick_line_width=1)

x_axis = CategoricalAxis(
    axis_label='securities',
    major_label_orientation = math.pi/4,
    **AXIS_FORMATS)

y_axis = LinearAxis(
    axis_label='% change',
    **AXIS_FORMATS)

plot.add_layout(x_axis, 'below')
plot.add_layout(y_axis, 'left')

_text_source = ColumnDataSource({'time': [_data.columns[0]]})
_text = Text(x=0.7, y=_y_min, text='time', text_font_size='60pt', text_color='#EEEEEE')
_text_renderer = plot.add_glyph(_text_source, _text)

vol_size_fator = 50/_data_vol.values.max()
_d = {
        'x':list(_data.index),
        'y':list(_data.iloc[:,0]),
        'color': [_color_map[_i] for _i in list(_data.index)],
        'size':list(_data_vol.iloc[:,0]*vol_size_fator)
}
_renderer_source = ColumnDataSource(_d)
_circle_glyph = Circle(
    x='x', y='y', size='size',
    fill_color='color', fill_alpha=0.8,
    line_color='#7c7e71', line_width=0.5, line_alpha=0.5)
_circle_renderer = plot.add_glyph(_renderer_source, _circle_glyph)


# plot slider
_max = _data.shape[1] - 1
_speed = 150
_slider = Slider(start=0,end=_max,step=1,value=0,width=600)
_slider.on_change('value', slider_update)
_slider.title = 'Time'

# the play button besides the slider
button = Button(label='► Play', width=60)
button.on_click(animate)

# organize the widgets and plots, then plot
pselect = widgetbox(_dropdown, _select, _select_button)
curdoc().add_root(row(pselect, column(plot, row(_slider, button))))