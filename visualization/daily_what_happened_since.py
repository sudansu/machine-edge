
# coding: utf-8

# In[1]:

#from IPython.display import HTML
#
#HTML('''<script>
#code_show=true;
#function code_toggle() {
# if (code_show){
# $('div.input').hide();
# } else {
# $('div.input').show();
# }
# code_show = !code_show
#}
#$( document ).ready(code_toggle);
#</script>
#<form action="javascript:code_toggle()"><input type="submit" value="Click here to #toggle on/off the raw code."></form>''')


# In[2]:

import codecs, math, functools

import pandas as pd
from pandas.tseries.offsets import BDay
import redis

#from ipywidgets import (
#    SelectMultiple, Dropdown, Button, IntSlider, Play, jslink, interactive, VBox, HBox
#)
#from IPython.display import display

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

def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)

def ChangeTimeSince(new=None):
    global _data, _data_vol
    global plot
    _dropdown.value=new
    _dropdown.label=new
    _s = int(_dt_rng_dict[new].timestamp())
    _zset = db.zrangebyscore('daily_zset',_s,math.inf, withscores=True) #db
    _zset_df = pd.DataFrame(_zset)

    _time_index = _zset_df[1].map(functools.partial(pd.to_datetime, unit='s'))
    _time_index.name='time'
    _cols = [_+':close' for _ in tuple(_select.value)]
    _sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

    _data = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
    _data.index = _data.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
    _data = _data.fillna(method='ffill').fillna(method='bfill').applymap(float)
    _data = (_data / _data.iloc[0] - 1) * 100
    _data = _data.T

    _cols = [_+':vol30' for _ in _select.value]
    _sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

    _data_vol = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
    _data_vol.index = _data_vol.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
    _data_vol = _data_vol.fillna(method='ffill').fillna(method='bfill').applymap(float)
    _data_vol = _data_vol.T

    _text_source.data['time'] = [_data.columns[_slider.value]]


def ChangeSelection():
    print(_select.value)
    global _data, _data_vol
    _cols = [_+':close' for _ in tuple(_select.value)]
    _sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

    _data = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
    _data.index = _data.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
    _data = _data.fillna(method='ffill').fillna(method='bfill').applymap(float)
    _data = (_data / _data.iloc[0] - 1) * 100
    _data = _data.T

    _cols = [_+':vol30' for _ in _select.value]
    _sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

    _data_vol = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
    _data_vol.index = _data_vol.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
    _data_vol = _data_vol.fillna(method='ffill').fillna(method='bfill').applymap(float)
    _data_vol = _data_vol.T

    #update the xrange and yrange
    _x = list(_data.index)
    plot.x_range.factors = _x
    #_margin = 2 #percent
    #_y_min = _data.values.min()-_margin
    #_y_max = _data.values.max()+_margin
    #plot.y_range.start = _y_min
    #plot.y_range.end = _y_max

    #update the _max value
    global _max
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
    #_text_renderer.glyph.y=_y_min+_margin


def slider_update(attrname, old, new):
    i=_slider.value
    _circle_renderer.data_source.data['y']=list(_data.iloc[:,i])
    _circle_renderer.data_source.data['size']=list(_data_vol.iloc[:,i]*vol_size_fator)
    _text_renderer.data_source.data = ColumnDataSource({'time': [_data.columns[i]]}).data
    #push_notebook(handle=_target)

def animate_update():
    value = _slider.value + 1
    if value > _max:
        value = _slider.end
    _slider.value = value

db = redis.StrictRedis()
# output_notebook(INLINE)

# load securities list
_raw_list = list(db.smembers('daily_sect')) #db
_sec_list = list(map(codecs.decode, _raw_list))

# load securities grouping
_grp_raw_dict = db.hgetall('sect_grp') #db
_sec_grp_df = pd.DataFrame(_raw_list, columns = ['sec'])
_sec_grp_df['grp'] = _sec_grp_df['sec'].map(_grp_raw_dict)
_sec_grp_df = _sec_grp_df.applymap(codecs.decode).sort_values('grp')
# assign colors
_color_dict = dict(zip(_sec_grp_df['grp'].unique(),Spectral4))
_sec_grp_df['color'] = _sec_grp_df['grp'].map(_color_dict)
_color_map = dict(zip(list(_sec_grp_df['sec']),list(_sec_grp_df['color'])))

# prepare securities multiple select
_options = list(_sec_grp_df['sec'])
#_select = SelectMultiple(
#    options=_options,
#    value = (_options[0],)
#)
_select = MultiSelect(
    options=_options,
    value = _options,
    #value = [_options[10],],
    sizing_mode = "scale_both"
)

# prepare 'time since' list dropdown
_start = pd.to_datetime('today').tz_localize('UTC').tz_convert('Asia/Singapore') - 365 * BDay()
_end = pd.to_datetime('now').tz_localize('UTC').tz_convert('Asia/Singapore')
_dt_rng = pd.date_range(start=_start,end=_end,freq='B',tz='Asia/Singapore')
_dt_rng_strf = list(_dt_rng.strftime('%Y-%b-%d'))
_dt_rng_dict = dict(zip(_dt_rng_strf, _dt_rng))
#_dropdown = Dropdown(
#    options=_dt_rng_strf,
#    value=_dt_rng_strf[0]
#)
_menu = list(zip(_dt_rng_strf, _dt_rng_strf))
_dropdown = Dropdown(
    #options=_opt,
    menu=_menu,
    default_value=_dt_rng_strf[0],
    label=_dt_rng_strf[0]
)

## display(_dropdown, _select)
# curdoc().add_root(widgetbox(_dropdown, _select))

# retrieve data based on 'time since' and 'securities list'
_s = int(_dt_rng_dict[_dropdown.default_value].timestamp())
_zset = db.zrangebyscore('daily_zset',_s,math.inf, withscores=True) #db
_zset_df = pd.DataFrame(_zset)

_time_index = _zset_df[1].map(functools.partial(pd.to_datetime, unit='s'))
_time_index.name='time'
_cols = [_+':close' for _ in tuple(_select.value)]
_sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

_data = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
_data.index = _data.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
_data = _data.fillna(method='ffill').fillna(method='bfill').applymap(float)
_data = (_data / _data.iloc[0] - 1) * 100
_data = _data.T

_cols = [_+':vol30' for _ in _select.value]
_sec_data=[db.hmget(_t[0],_cols) for _t in _zset] #db

_data_vol = pd.DataFrame(_sec_data, columns = pd.Series(tuple(_select.value),name='sec'), index=_time_index)
_data_vol.index = _data_vol.index.tz_localize('UTC').tz_convert('Asia/Singapore').strftime('%Y-%b-%d')
_data_vol = _data_vol.fillna(method='ffill').fillna(method='bfill').applymap(float)
_data_vol = _data_vol.T

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

##_target = show(plot, notebook_handle=True)

_max = _data.shape[1] - 1
_speed = 150
##_slider = IntSlider(min=0,max=_max,step=1,value=0)
_slider = Slider(start=0,end=_max,step=1,value=0)
_slider.on_change('value', slider_update)
##_play = Play(interval=_speed,min=0,max=_max)
##jslink((_play, 'value'), (_slider, 'value'))
##_interact=interactive(update,i=_slider)
##_slider.description = ''
_slider.title = 'Time'

##HBox([_interact,_play])

# dropdown change since start point
_dropdown.on_click(ChangeTimeSince)

button = Button(label='► Play', width=60)
button.on_click(animate)

_select_button = Button(label='Apply', width=60)
_select_button.on_click(ChangeSelection)

pselect = widgetbox(_dropdown, _select, _select_button)
curdoc().add_root(column(pselect, plot, row(_slider, button)))
