from bokeh.plotting import figure, curdoc
from bokeh.models import HoverTool

from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from source import redis_io
from core import regime
from plot import FigureSource

redis_source = None
main_figure_src = None
option_dropdown = None
kTURB_THRESHOLD = 0.9
regime_analyzer = None

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
          a FigureSource instance that encapsulates the figure and its containing data source 
    '''
    circle_source = ColumnDataSource(data=dict(index=[], close=[],color=[],size = [],prob = []))
    line_source = ColumnDataSource(data=dict(index=[], close=[], color=[]))

    _tools = "pan,box_zoom,wheel_zoom, reset"
    _fig = figure(width=800, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    _fig.multi_line('index', 'close', source=line_source, color='color', line_width=1, line_alpha=1, legend='daily-close')
    _circle_renderer = _fig.circle('index', 'close', source=circle_source, color='color', size='size', legend='daily-close')

    # customize figure by setting attributes
    _fig.title.text = dropdown.default_value + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha=0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1

    hover = HoverTool(renderers=[_circle_renderer],point_policy = "follow_mouse",tooltips=[
        ("Price", "@close"),
        ("Turbulance Prob", "@prob"),
    ])
    _fig.add_tools(hover)
    _fig.add_tools(BoxSelectTool(dimensions=["width"]))

    fs = FigureSource(_fig)
    fs.add_source(circle_source)
    fs.add_source(line_source)
    return fs

def CreateSourceData(redis_src, option):
    '''Create data for main source and line source for option
    
       Args:
          redis_src: a RedisSource instance that provide data
          option: the selected currency to plot on graph
       
       Return:
           a tuple of two dict:(circle_source_data, line_source_data)
    '''
    _df = redis_src.data_frame(option)
    # print ("Creating Main Source: ")
    # print ("Type _dt.index")
    # print (type(_df.index))
    colors = ["navy"] * len(_df.index)
    probs = ["N.A."] * len(_df.index)
    sizes = [2] * len(_df.index)


    circle_source_data = dict(index=_df.index, close=_df.close,color=colors,size = sizes,prob = probs)

    idx_line = []
    close_line = []
    colors_line = []
    for i  in range(len(_df.index) - 1):
        idx_line.append([_df.index[i], _df.index[i+1]])
        close_line.append([_df.close[i], _df.close[i+1]])
        colors_line.append("navy")

    line_source_data = dict(index=idx_line, close=close_line, color=colors_line)
    return circle_source_data, line_source_data
    
def ChangeSource(new):
    '''The function to be triggered when users change data source in option dropdown
    
        The followings steps will go through:
            * Retieve all data for new option
            * Provide new data for regime analyzer
            * Replot the main figure using data
            
    Args:
        new: the string of newly selected data source, e.g, aud, sgd ...
    '''
    
    
    global main_figure_src
    global redis_source
    global regime_analyzer
    
    _df = redis_src.data_frame(option)
    regime_analyzer.fit(_df.close)
    main_figure_src.fig.title.text = new + " (daily)"
    circle_data, line_data = CreateSourceData(redis_source, new)
    main_figure_src[0].data = circle_data
    main_figure.src[1].data = line_data

def Analyze():
    ''' The function to be triggered when clicking the analysis button
    
    Following steps to be done:
      * get turbulance probability
      * Change main figure's circle and line color based on turbulance probability and threshold
    '''
    
    global regime_analyzer
    global main_figure_src
    global option_dropdown
    global redis_source
    global kTURB_THRESHOLD 
    
    turb_probs = regime_analyzer.predict()
    
    length = len(main_figure_src.srcs[0].data['index'])    
    colors = ["navy"] * length
    
    for i, turb_prob in enumerate(turb_probs):
        if turb_prob > kTURB_THRESHOLD:
            colors[i] = "red"
            
    main_figure_src.srcs[0].data['colors'] = colors
    line_colors = ["navy"] * (length - 1)

    for i in range(len(turb_probs) - 1):
        if turb_probs[i] > kTURB_THRESHOLD and turb_probs[i+1] > kTURB_THRESHOLD:
            line_colors[i] = "red"  
            
    main_figure_src.srcs[1].data['colors'] = colors
    
def main():
    '''Main program to execute when server starts up
    
    Steps:
        * Create figures, widgets, redis source and regime analyzer and make them global
        * Arrange the figures and plot
        * Populate data for graph to display
    '''
    global redis_source
    global regime_analyzer
    global main_figure_src
    global option_dropdown
    
    redis_source = redis_io.RedisSource()
    option_dropdown = CreateDropdown(redis_source.options())
    main_figure_src = CreateMainFigure()
    regime_analyzer = regime.RegimeShiftPrediction()
    
    option_dropdown.on_click(ChangeSource)
    
    button = Button(label="Analyze!", button_type="warning")
    button.on_click(Analyze)
    
    main_plot = row(main_figure_src.fig, widgetbox(option_dropdown, button))
    curdoc().add_root(main_plot)
    
    #Populate the graph
    ChangeSource(option_dropdown.value)
