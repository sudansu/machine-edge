import numpy as np
import pandas as pd
import redis, codecs

from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.layouts import gridplot, widgetbox, row
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.models.widgets import Dropdown
from bokeh.embed import components

def redis_plot():
    # prepare some data
    db = redis.StrictRedis()
    _g = db.hgetall('sect_grp')
    _s = pd.Series(list(db.smembers('daily_sect')))
    _grp_map = pd.DataFrame({'sect':_s,'grp':_s.map(_g)}).applymap(codecs.decode)
    # read entire time-series from redis with timestamp in epoch format
    _df = pd.DataFrame(db.zrange('daily_zset', 0, -1, withscores=True))
    _ts = _df[0]
    # convert from utc to Singapore time by +8 hours
    _ts.index = pd.Series(pd.to_datetime(_df[1], unit='s')) + pd.Timedelta('8 hours')
    _ts.index.name = 'date'

    _opt = sorted(list(_grp_map['sect']))

    menu = list(zip(_opt, _opt))

    dropdown = Dropdown(label=_opt[0], button_type="success", menu=menu, default_value=_opt[0])

    def get_data(sec):
        flds = ['open','high','low','close']
        _cols = ['{}:{}'.format(sec, _) for _ in flds]
        _data = [db.hmget(_, _cols) for _ in _ts]
        df = pd.DataFrame(_data, columns=flds, index=_ts.index).dropna().applymap(float)
        return df

    df = get_data(dropdown.default_value)
    source = ColumnDataSource(data=dict(index=df.index, low=df.low, high=df.high))

    # output to static HTML file
    # output_file("redis_demo.html", title="redis demo")

    # create a new plot with a datatime axis type
    p = figure(width=800, height=350, x_axis_type="datetime", webgl=True)

    def update_source(new):
        p.title.text = new + " (daily)"
        dropdown.label = new
        df = get_data(new)
        new_source = ColumnDataSource(data=dict(index=df.index, low=df.low, high=df.high))
        source.data = new_source.data

    # add renderers
    # p.circle(aapl_dates, aapl, size=4, color='darkgrey', alpha=0.2, legend='close')
    p.line('index', 'high', source=source, color='navy', legend='daily-high')
    p.line('index', 'low', source=source, color='firebrick', legend='daily-low')
    # p.line(df.index, df.low, color='firebrick', legend='daily-low')
    # p.line(aapl_dates, aapl_avg, color='navy', legend='avg')

    # NEW: customize by setting attributes
    p.title.text = dropdown.default_value + " (daily)"
    p.legend.location = "top_left"
    p.grid.grid_line_alpha=0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.ygrid.band_fill_color="olive"
    p.ygrid.band_fill_alpha=0.1
    dropdown.on_click(update_source)

    return components(p)

# show the results
# plot = gridplot([[p, dropdown]])
# plot = row(p, dropdown)
# show(plot)
# curdoc().add_root(plot)

