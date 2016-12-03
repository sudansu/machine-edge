from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button

from source import redis_io
from core import knn

redis_source = None
main_figure = None
knn_figures = None
predict_figure = None

# global configuration
look_ahead = 3
kNUM_KNN = 5
kNUM_SHOW = 5

def CreateDropdown(_options):
    '''Create the dropdown to select data source, e.g, aud, sgd ...
    
        Args:
            options: a list of data source to choose from
        Return:
            a bokeh dropdown widget
    '''
    _menu = list(zip(_options, _options))
    return Dropdown(label=_options[0], button_type="success", menu=_menu, default_value=_options[0])

def CreateMainFigure():
    '''Create Main Figure without any data
    
        Return:
          a bokeh figure
    '''
    main_source = ColumnDataSource(data=dict(index=[], close=[]))
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

def CreateKnnFigures():
    '''Create kNUM_SHOW figures to show most similar segments of the selected points in main figure.
    
      Each figure source is empty at the creation time and source data will be populated when users click the prediciton buttonn
      
      Return: 
          a list of kNUM_SHOW bokeh figures, with i-th one shows the the i-th similar segment
     '''
    _knn_fig = list()
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
        _knn_fig.append(_fig)
    return _knn_fig

def CreatePredictFigure():
    '''Create Figure to show future currency value prediction
        
        The figure is initiated without data when created. Data will be populated when users click the prediction button. 
    
        Return:
          a bokeh figure
    '''
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
    return _fig
    
def UpdateMainFigure(main_figure, redis_source, option):
    '''Update the data shown on main figure based on the option
    
    Args:
        main_figure: main Bokeh figure to be updated
        redis_source: a RedisSource instance to provide data
        option: the currency whose value will be plotted
     '''
     
     #Get all data for option
     _df = redis_source.data_frame(option)
     _new_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close))
     main_figure.line.source = _new_source
     main_figure.line.source = _new_source
     
     main_figure.title.text = option + " (daily)"

def UpdateKnnFigure(knn_fig, redis_src, option, inds_min, indx_max):
    '''Update the data shown on one knn figure based on the option currency value in a range
    
        Args:
            knn_fig: the knn bokeh figure to be updated for display
            redis_src: a RedisSource instance to provide data
            option: the currency whose value will be plotted
            indx_min: the start index of the range
            indx_max: the end index of the range
     '''
    _df = redis_source.data_frame(option)
    _d2 = knn_fig.line.source.data
    _d3 = knn_fig.circle.source.data
    _src_len = inds_max - inds_min
    _start = max(0, inds_min - _src_len//2)
    _end = inds_max + _src_len//2
    _d2['index'] = _df.index[_start:_end]
    _d2['close'] = _df.close[_start:_end]
    _d3['index'] = _df.index[inds_min:inds_max]
    _d3['close'] = _df.close[inds_min:inds_max]
    
def UpdatePredictFigure(predict_fig, redis_src, option, inds_min, indx_max, mean_rates, stv_rate):
    '''Update the data shown on the prediction figure based on the option currency value in a range
    
        Args:
            predict_fig: the prediction bokeh figure to be updated for display
            redis_src: a RedisSource instance to provide data
            option: the currency whose value will be plotted
            indx_min: the start index of the range
            indx_max: the end index of the range
            mean_rates: a list of mean change rates for predicted look_ahead points
            stv_rates: a list of stdv change rate for predicted look_ahead points
     '''
    _df = redis_source.data_frame(option)
    _old_index = list(_df.index[inds_min:inds_max])
    _old_close = list(_df.close[inds_min:inds_max])    

    _step = _df.index[inds_min+1] - _df.index[inds_min]

    _d2 = predict_fig.line.data #line source
    _d3 = predict_fig.circle.data #current source (Circle)
    _d4 = predict_fig.patch.data #future source (Patch)

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
   
    _d4['index'] = future_index
    _d4['close'] = future_close
