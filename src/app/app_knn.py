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
