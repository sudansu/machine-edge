from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button

from datasource import DataSource
from prediction import KnnPrediction

def CreateDropdown():
    _options = sources.Options()
    _menu = list(zip(_options, _options))
    return Dropdown(label=_options[0], button_type="success", menu=_menu, default_value=_options[0])

def CreateMainSource():
    _df = sources.GetDataFrame(dropdown.default_value)
    return ColumnDataSource(data=dict(index=_df.index, close=_df.close))

def CreateMainFigure():
    _tools = "pan,box_zoom,wheel_zoom,reset"
    _fig = figure(width=800, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    _fig.line('index', 'close', source=main_source, color='navy', line_alpha=0.5, legend='daily-close')
    _renderer = _fig.circle('index', 'close', source=main_source, color='navy', size=2, legend='daily-close')
    # set select/unselect color
    _selected_circle = Circle(fill_alpha=1, fill_color="firebrick", size=3, line_alpha=1,  line_color="firebrick")
    _nonselected_circle = Circle(fill_alpha=0, fill_color="navy", size=2, line_alpha=0, line_color="navy")
    _renderer.selection_glyph = _selected_circle
    _renderer.nonselection_glyph = _nonselected_circle
    # customize figure by setting attributes
    _fig.title.text = dropdown.default_value + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha=0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1
    return _fig

def CreateKnnFigure():
    # add 5 knn figures
    _knn_fig = list()
    _knn_source = list()
    for i in range(0, kNUM_KNN):
        # fig = figure(width=200, height=200, x_axis_type="datetime", webgl=True)
        _fig = figure(width=200, height=200, x_axis_type="datetime", webgl=True, tools=[], toolbar_location=None)
        _line_source = ColumnDataSource(data=dict(index=[], close=[]))
        _fig.line('index', 'close', source=_line_source, color='navy')
        _circle_source = ColumnDataSource(data=dict(index=[], close=[]))
        _fig.circle('index', 'close', source=_circle_source, color='firebrick', size=3)
        _fig.title.text = "Top " + str(i+1) + " Nearest Neighbor"
        _fig.title.align = "center"
        _fig.grid.grid_line_alpha=0
        _fig.ygrid.band_fill_color="olive"
        _fig.ygrid.band_fill_alpha=0.1
        _knn_source.append([_line_source, _circle_source])
        _knn_fig.append(_fig)
    return _knn_fig, _knn_source

def ChangeSource(new):
    main_fig.title.text = new + " (daily)"
    dropdown.label = new
    _df = sources.GetDataFrame(new)
    _new_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close))
    main_source.data = _new_source.data
    knn_pred.SetSource(main_source.data['close'])

def UpdateKnnSource(line_src, circle_src, inds_min, inds_max):
    _d1 = main_source.data
    _d2 = line_src.data
    _d3 = circle_src.data
    _src_len = inds_max - inds_min
    _start = max(0, inds_min - _src_len//2)
    _end = inds_max + _src_len//2
    _d2['index'] = _d1['index'][_start:_end]
    _d2['close'] = _d1['close'][_start:_end]
    _d3['index'] = _d1['index'][inds_min:inds_max]
    _d3['close'] = _d1['close'][inds_min:inds_max]

def UpdatePredictSource(src, inds_min, inds_max, avg_v, min_v, max_v):
    _d1 = main_source.data
    _all_index = _d1['index'][inds_min:inds_max]
    _all_close = _d1['close'][inds_min:inds_max]
    _old_index = _d1['index'][inds_min:inds_max]
    _old_close = _d1['close'][inds_min:inds_max]
    _new_index = _d1['index'][inds_min:inds_min]
    _new_close = _d1['close'][inds_min:inds_min]
    _min_index = _d1['index'][inds_min:inds_min]
    _min_close = _d1['close'][inds_min:inds_min]
    _max_index = _d1['index'][inds_min:inds_min]
    _max_close = _d1['close'][inds_min:inds_min]
    _step = _d1['index'][inds_min+1] - _d1['index'][inds_min]
    for i in range(0, len(avg_v)):
        _rate = avg_v[i]
        _s = _all_index[-1] + _step
        _v = _all_close[-1] * _rate
        _all_index.append(_s)
        _new_index.append(_s)
        _min_index.append(_s)
        _max_index.append(_s)
        _all_close.append(_v)
        _new_close.append(_v)
        _min_close.append(_v / _rate * min_v[i])
        _max_close.append(_v / _rate * max_v[i])
    _d2 = src[0].data
    _d3 = src[1].data
    _d4 = src[2].data
    _d5 = src[3].data
    _d6 = src[4].data
    _d2['index'] = _all_index
    _d2['close'] = _all_close
    _d3['index'] = _old_index
    _d3['close'] = _old_close
    _d4['index'] = _new_index
    _d4['close'] = _new_close
    _d5['index'] = _min_index
    _d5['close'] = _min_close
    _d6['index'] = _max_index
    _d6['close'] = _max_close

def Predict():
    # find selected start/end points
    _inds = sorted(main_source.selected['1d']['indices'])
    # skip if none
    if (len(_inds) == 0):
        return
    _inds_min = _inds[0]
    _inds_max = _inds[-1] + 1
    _w = knn_pred.GetTopKnn(_inds_min, _inds_max, kNUM_KNN)
    print(_w)
    # update knn fig
    for i in range(0, len(_w)):
        _src = knn_source[i]
        UpdateKnnSource(_src[0], _src[1], _w[i][1], _w[i][1] + _inds_max - _inds_min)
        knn_fig[i].title.text = "Top " + str(i+1) + " NN dist(" + format(_w[i][0], '.5f') + ")"
    # update pred fig
    _avg, _min, _max = knn_pred.Predict(_inds_min, _inds_max, _w)
    UpdatePredictSource(predict_source, _inds_min, _inds_max, _avg, _min, _max)

def CreatePredictFigure():
    _fig = figure(width=300, height=300, x_axis_type="datetime", webgl=True, tools=[], toolbar_location=None)
    _line_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.line('index', 'close', source=_line_source, color='navy')
    _current_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_current_source, color='firebrick', size=3)
    _future_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_future_source, color='olive', size=5)
    _min_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_min_source, color='navy', size=3)
    _max_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_max_source, color='navy', size=3)
    _fig.title.text = "Predicted Trend"
    _fig.title.align = "center"
    _fig.grid.grid_line_alpha=0
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1
    _source = [_line_source, _current_source, _future_source, _min_source, _max_source]
    return _fig, _source

# global configuration
kNUM_KNN = 5
# get data sources
sources = DataSource()
# add widgets
dropdown = CreateDropdown()
# get main source
main_source = CreateMainSource()
# create knn prediction
knn_pred = KnnPrediction()
knn_pred.SetSource(main_source.data['close'])
# draw main figure
main_fig = CreateMainFigure()
# draw knn figure
knn_fig, knn_source = CreateKnnFigure()
# add box select tool
main_fig.add_tools(BoxSelectTool(dimensions=["width"]))
# add dropdown on click actions
dropdown.on_click(ChangeSource)
# add button for prediction
button = Button(label="Predict!", button_type="warning")
button.on_click(Predict)
# draw predict figure
predict_fig, predict_source = CreatePredictFigure()

# show figures
pred_plot = column(widgetbox(dropdown, button), predict_fig)
main_plot = row(main_fig, pred_plot)
knn_plot = row(knn_fig)
plot = column(main_plot, knn_plot)
curdoc().add_root(plot)
