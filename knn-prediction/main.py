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
    # print ("Creating Main Source: ")
    # print ("Type _dt.index")
    # print (type(_df.index))
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
    for i in range(0, kNUM_SHOW):
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
    # print ("Change Source: ")
    # print ("Type of main source data index")
    # print (type(main_source.data["index"]))
    knn_pred.SetSource(main_source.data['close'])
    # Clear the source for knn figures
    for i in range(0, kNUM_SHOW):
        _src = knn_source[i]
        _d1 = _src[0].data
        _d2 = _src[1].data
        knn_fig[i].title.text = "Top " + str(i+1) + " NN"
        _d1['index'] = []
        _d1['close'] = []
        _d2['index'] = []
        _d2['close'] = []
    
    #clear the source for prediction figure
    src = predict_source
    _d2 = src[0].data #line source
    _d3 = src[1].data #current source
    _d4 = src[2].data #future source
    _d5 = src[3].data #min source
    _d6 = src[4].data #max sourcs
    _d2['index'] = []
    _d2['close'] = []
    _d3['index'] = []
    _d3['close'] = []
    _d4['index'] = []
    _d4['close'] = []
    _d5['index'] = []
    _d5['close'] = []
    _d6['index'] = []
    _d6['close'] = []

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
    # print ("Start Updating Predict Source")
    _d1 = main_source.data
    # print()
    # print("type(_d1['index'])")
    # print(type(_d1['index']))
    # print()
    # print("type(_d1['index'][inds_min:inds_max]))")
    # print(type(_d1['index'][inds_min:inds_max]))

    _all_index = list(_d1['index'][inds_min:inds_max])
    _all_close = list(_d1['close'][inds_min:inds_max])
    _old_index = list(_d1['index'][inds_min:inds_max])
    _old_close = list(_d1['close'][inds_min:inds_max])
    # _new_index = _d1['index'][inds_min:inds_min]
    # _new_close = _d1['close'][inds_min:inds_min]
    # _min_index = _d1['index'][inds_min:inds_min]
    # _min_close = _d1['close'][inds_min:inds_min]
    # _max_index = _d1['index'][inds_min:inds_min]
    # _max_close = _d1['close'][inds_min:inds_min]
    _new_index = []
    _new_close = []
    _min_index = []
    _min_close = []
    _max_index = []
    _max_close = []
    _step = _d1['index'][inds_min+1] - _d1['index'][inds_min]

    # print ("Before updating source")
    # print("all_index- Len:  " + str(len(_all_index)))
    # print (_all_index)
    # print()
    # print("all_close- Len:  " + str(len(_all_close)))
    # print (_all_close)
    # print()
    # print("old_index- Len:  " + str(len(_old_index)))
    # print(_old_index)
    # print()
    # print("old_close- Len:  " + str(len(_old_close)))
    # print (_old_close)
    # print()
    # print("new_index- Len:  " + str(len(_new_index)))
    # print(_new_index)
    # print()
    # print("new_close- Len:  " + str(len(_new_close)))
    # print (_new_close)
    # print()
    # print("min_index- Len:  " + str(len(_min_index)))
    # print(_min_index)
    # print()
    # print("min_close- Len:  " + str(len(_min_index)))
    # print (_min_close)
    # print()
    # print("max_index- Len:  " + str(len(_max_index)))
    # print(_max_index)
    # print()
    # print("max_close- Len:  " + str(len(_max_close)))
    # print (_max_close)
    # print()

    # print("_step = ")
    # print(_step)
    # print(type(_step))
    # print()
    # print("Avg_v: ")
    # print(avg_v)
    # print()
    # print("min_v: ")
    # print(min_v)
    # print()
    # print("Max_v: ")
    # print(max_v)
    # print()


    for i in range(0, len(avg_v)):
        _rate = avg_v[i]
        # print("_rate = " + str(_rate))
        _s = _all_index[-1] + _step
        # print("_s = ")
        # print(_s)
        # print(type(_s))
        _v = _all_close[-1] * _rate
        # print("_v = " + str(_v))
        _all_index.append(_s)
        _new_index.append(_s)
        _min_index.append(_s)
        _max_index.append(_s)
        _all_close.append(_v)
        _new_close.append(_v)
        _min_close.append(_v / _rate * min_v[i])
        _max_close.append(_v / _rate * max_v[i])

    print("Finish Loop")
    _d2 = src[0].data #line source
    _d3 = src[1].data #current source (Circle)
    _d4 = src[2].data #future source (Circle)
    _d5 = src[3].data #min source (Circle)
    _d6 = src[4].data #max sourcs (Circle)

    # print("After updating source: ")
    # print("all_index- Len:  " + str(len(_all_index)))
    # print (_all_index)
    # print()
    # print("all_close- Len:  " + str(len(_all_close)))
    # print (_all_close)
    # print()
    # print("old_index- Len:  " + str(len(_old_index)))
    # print(_old_index)
    # print()
    # print("old_close- Len:  " + str(len(_old_close)))
    # print (_old_close)
    # print()
    # print("new_index- Len:  " + str(len(_new_index)))
    # print(_new_index)
    # print()
    # print("new_close- Len:  " + str(len(_new_close)))
    # print (_new_close)
    # print()
    # print("min_index- Len:  " + str(len(_min_index)))
    # print(_min_index)
    # print()
    # print("min_close- Len:  " + str(len(_min_index)))
    # print (_min_close)
    # print()
    # print("max_index- Len:  " + str(len(_max_index)))
    # print(_max_index)
    # print()
    # print("max_close- Len:  " + str(len(_max_close)))
    # print (_max_close)
    # print()
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

def Update_GP_Predict_Source(src, inds_min, inds_max,mean_rates,stv_rate):
    print("mean_rates: ")
    print(mean_rates)
    print("stv_rate: ")
    print(stv_rate)

    _d1 = main_source.data

    _old_index = list(_d1['index'][inds_min:inds_max])
    _old_close = list(_d1['close'][inds_min:inds_max])    

    _step = _d1['index'][inds_min+1] - _d1['index'][inds_min]

    _d2 = src[0].data #line source
    _d3 = src[1].data #current source (Circle)
    _d4 = src[2].data #future source (Patch)

    _d2['index'] = _old_index
    _d2['close'] = _old_close   
    _d3['index'] = _old_index
    _d3['close'] = _old_close   

    future_index = []
    future_close = []
    future_index.append(_old_index[-1])
    future_close.append(_old_close[-1])

    pre_close = _old_close[-1]
    for i in range(1,look_ahead+1):
        _s = _old_index[-1] + _step * i
        future_index.append(_s)
        future_close.append(pre_close * (mean_rates[i - 1] + stv_rate))

    for i in range(look_ahead,0,-1):
        _s = _old_index[-1] + _step * i
        future_index.append(_s)
        future_close.append(pre_close * (mean_rates[i - 1] - stv_rate))
    
    print("Future Index: ")
    print(future_index)
    print("Future Close: ")
    print(future_close)
    print()
    _d4['index'] = future_index
    _d4['close'] = future_close


def Predict(): # find selected start/end points
    _inds = sorted(main_source.selected['1d']['indices'])
    # skip if none
    if (len(_inds) == 0):
        return
    _inds_min = _inds[0]
    _inds_max = _inds[-1] + 1

    # print ("_inds_min")
    # print (_inds_min)

    # print("_inds_max")
    # print(_inds_max)
    _w = knn_pred.GetTopKnn(_inds_min, _inds_max, kNUM_KNN)
    print(_w)
    # update knn fig
    for i in range(0, kNUM_SHOW):
        _src = knn_source[i]
        UpdateKnnSource(_src[0], _src[1], _w[i][1], _w[i][1] + _inds_max - _inds_min)
        knn_fig[i].title.text = "Top " + str(i+1) + " NN dist(" + format(_w[i][0], '.5f') + ")"
    # update pred fig
    # _avg, _min, _max = knn_pred.Predict(_inds_min, _inds_max, _w)
    mean_rates,stv_rate = knn_pred.GP_Predict(_inds_min, _inds_max, _w,look_ahead)
    Update_GP_Predict_Source(predict_source, _inds_min, _inds_max,mean_rates,stv_rate)
    # UpdatePredictSource(predict_source, _inds_min, _inds_max, _avg, _min, _max)

def Create_GP_Predict_Figure():

    _fig = figure(width=300, height=300, x_axis_type="datetime", webgl=True, tools=[], toolbar_location=None)
    _line_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.line('index', 'close', source=_line_source, color='navy')
    _current_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_current_source, color='firebrick', size=3)
    _future_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.patch('index', 'close', source=_future_source, alpha=0.5, color="#99d8c9")
    _fig.title.text = "GP Predicted Trend"
    _fig.title.align = "center"
    _fig.grid.grid_line_alpha=0
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1
    _source = [_line_source, _current_source, _future_source ]
    return _fig, _source

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
look_ahead = 3
kNUM_KNN = 10
kNUM_SHOW = 5
# get data sources
sources = DataSource()
# add widgets
dropdown = CreateDropdown()
# get main source
main_source = CreateMainSource()
# create knn prediction
# print ("Main Source: ")
# print ("Type of main source data index")
# print (type(main_source.data["index"]))

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
# predict_fig, predict_source = CreatePredictFigure()

predict_fig, predict_source = Create_GP_Predict_Figure()
# show figures
pred_plot = column(widgetbox(dropdown, button), predict_fig)
main_plot = row(main_fig, pred_plot)
knn_plot = row(knn_fig)
plot = column(main_plot, knn_plot)
curdoc().add_root(plot)
