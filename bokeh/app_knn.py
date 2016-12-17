from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button

from source import redis_io
from core import knn
from plot.figure_source import FigureSource

redis_source = None
main_figure_src = None
knn_figure_srcs = None
predict_figure_src = None
option_dropdown = None
# global configuration
kLOOK_AHEAD = 3
kNUM_KNN = 5
kNUM_SHOW = 5

#engine for prediction
knn_predictor = None

def CreateDropdown(_options):
    '''Create the dropdown to select data source, e.g, aud, sgd ...

        Args:
            options: a list of data source to choose from
        Return:
            a bokeh dropdown widget
    '''
    _menu = list(zip(_options, _options))
    return Dropdown(label=_options[0], button_type="success", menu=_menu, default_value=_options[0],value=_options[0])

def CreateMainFigure():
    '''Create Main Figure without any data

        Return:
          a FigureSource instance that encapsulates the figure and its source
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
    _fig.title.text = option_dropdown.default_value + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha=0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1
    _fig.add_tools(BoxSelectTool(dimensions=["width"]))

    fs = FigureSource(_fig)
    fs.add_source(main_source)
    return fs

def CreateKnnFigures():
    '''Create kNUM_SHOW figures to show most similar segments of the selected points in main figure.

      Each figure source is empty at the creation time and source data will be populated when users click the prediciton buttonn

      Return:
          a list of kNUM_SHOW bokeh figures, with i-th one shows the the i-th similar segment
     '''

    knn_figure_srcs = []
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

        fs = FigureSource(_fig)
        fs.add_source(_line_source)
        fs.add_source(_circle_source)
        knn_figure_srcs.append(fs)
    return knn_figure_srcs

def CreatePredictFigure():
    '''Create Figure to show future currency value prediction

        The figure is initiated without data when created. Data will be populated when users click the prediction button.

        Return:
          a FigureSource instance
    '''
    _fig = figure(width=300, height=300, x_axis_type="datetime", webgl=True, tools=[], toolbar_location=None)
    _line_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.line('index', 'close', source=_line_source, color='navy')

    _current_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_current_source, color='firebrick', size=3)

    _future_patch_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.patch('index', 'close', source=_future_patch_source, alpha=0.5, color="#99d8c9")

    _future_circle_source = ColumnDataSource(data=dict(index=[], close=[]))
    _fig.circle('index', 'close', source=_future_circle_source, color="red", size=5)

    _fig.title.text = "GP Predicted Trend"
    _fig.title.align = "center"
    _fig.grid.grid_line_alpha=0
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1

    fs = FigureSource(_fig)
    fs.add_source(_line_source)
    fs.add_source(_current_source)
    fs.add_source(_future_patch_source)
    fs.add_source(_future_circle_source)
    return fs

def UpdateMainFigure(fig_src, df):
    '''Update the data shown on main figure based on the option

    Args:
        figure_src: main Bokeh figure source to be updated
        df: panda data frame that provides close price and datetime
     '''

     #Get all data for option

    fig_src.srcs[0].data['index'] = df.index
    fig_src.srcs[0].data['close'] = df.close

def UpdateKnnFigure(knn_fig_src, df, inds_min, inds_max):
    '''Update the data shown on one knn figure based on the option currency value in a range

        Args:
            knn_fig_src: the knn FigureSource to be updated to be updated for display
            df: panda dataframe instance that provide the all close price and datetime
            indx_min: the start index of the range
            indx_max: the end index of the range
     '''

    _d2 = knn_fig_src.srcs[0].data
    _d3 = knn_fig_src.srcs[1].data

    _src_len = inds_max - inds_min
    _start = max(0, inds_min - _src_len//2)
    _end = inds_max + _src_len//2

    _d2['index'] = df.index[_start:_end]
    _d2['close'] = df.close[_start:_end]
    _d3['index'] = df.index[inds_min:inds_max]
    _d3['close'] = df.close[inds_min:inds_max]

def UpdatePredictFigure(predict_fig_src, df, inds_min, inds_max, preds, preds_std):
    '''Update the data shown on the prediction figure based on the option currency value in a range

        Args:
            predict_fig_src: the prediction figure source to be updated for display
            df: panda dataframe that provide a currency's all close price and datetime
            indx_min: the start index of the range
            indx_max: the end index of the range
            mean_rates: a list of values for predicted look_ahead points
            stv_rates: a value of stdv for predicted look_ahead points
     '''

    _old_index = list(df.index[inds_min:inds_max])
    _old_close = list(df.close[inds_min:inds_max])

    _step = df.index[inds_min+1] - df.index[inds_min]

    _d2 = predict_fig_src.srcs[0].data #line source
    _d3 = predict_fig_src.srcs[1].data #current source (Circle)
    _d4 = predict_fig_src.srcs[2].data #future patch source 
    _d5 = predict_fig_src.srcs[3].data #future circle source

    _d2['index'] = _old_index
    _d2['close'] = _old_close
    _d3['index'] = _old_index
    _d3['close'] = _old_close

    future_index = []
    future_close = []
    future_index.append(_old_index[-1])
    future_close.append(_old_close[-1])

    pre_close = _old_close[-1]
    for i in range(1,kLOOK_AHEAD + 1):
        _s = _old_index[-1] + _step * i
        future_index.append(_s)
        future_close.append(preds[i-1] + preds_std)

    for i in range(kLOOK_AHEAD,0,-1):
        _s = _old_index[-1] + _step * i
        future_index.append(_s)
        future_close.append(preds[i-1] - preds_std)

    _d4['index'] = future_index
    _d4['close'] = future_close

    future_circle_index = []
    future_circle_close = []
    for i in range(1,kLOOK_AHEAD + 1):
        _s = _old_index[-1] + _step * i
        future_circle_index.append(_s)
        future_circle_close.append(preds[i-1])
    _d5['index'] = future_circle_index
    _d5['close'] = future_circle_close

def Predict():
    '''A handler to execute when clicking the prediction button

    Several things to do:
        * Get the selected points
        * Get a list of similar segments for selected points
        * Update one knn figure for each similar segment in the order of similarity
        * Predict the mean and stdv of change rates based on the similar segments
        * Update the prediction figure accordingly
    '''

    global main_figure_src
    global knn_figure_srcs
    global predict_figure_src
    global redis_source

    _inds = sorted(main_figure_src.srcs[0].selected['1d']['indices'])
    # skip if none
    if (len(_inds) == 0):
        return

    _inds_min = _inds[0]
    _inds_max = _inds[-1] + 1

    # _w a list of tuples. The list contains kNUM_KNN tuples.
    # Each tuple has 2 elements.
    #   The first element is the distance.
    #   The second element is the start index of the similar segment.
    _w = knn_predictor.get_knn(_inds_min, _inds_max, kNUM_KNN)
    # print(_w)
    # update knn fig
    option = option_dropdown.value
    for i in range(0, kNUM_SHOW):
        knn_fig_src = knn_figure_srcs[i]
        seg_indx_min = _w[i][1]
        seg_indx_max = _w[i][1]  + _inds_max - _inds_min

        knn_df = redis_source.data_frame(option)
        UpdateKnnFigure(knn_fig_src, knn_df, seg_indx_min, seg_indx_max)

        knn_fig_src.fig.title.text = "Top " + str(i+1) + " NN dist(" + format(_w[i][0], '.5f') + ")"

    # update pred fig
    # _avg, _min, _max = knn_pred.Predict(_inds_min, _inds_max, _w)
    mean_rates,stv_rate = knn_predictor.predict(_inds_min, _inds_max, _w,kLOOK_AHEAD)
    # print('mean: ', mean_rates)
    # print('stdv: ', stv_rates)

    predict_df = redis_source.data_frame(option)
    UpdatePredictFigure(predict_figure_src, predict_df, _inds_min, _inds_max,mean_rates,stv_rate)

def ChangeSource(new):
    '''The function to be triggered when users change data source in option dropdown

        The followings step will go through:
            * Retieve all data for new option
            * Provide new data for knn predictor
            * Update the data for main figure and replot
            * Clear all the data in knn figures and prediction figures

    Args:
        new: the string of newly selected data source, e.g, aud, sgd ...
    '''

    global main_figure_src
    global redis_source
    global knn_predictor
    global knn_figure_srcs
    global predict_figure_src

    df = redis_source.data_frame(new)
    knn_predictor.fit(df.close)

    main_figure_src.fig.title.text = new + " (daily)"
    option_dropdown.label = new

    UpdateMainFigure(main_figure_src, df)

    # print ("Change Source: ")
    # print ("Type of main source data index")
    # print (type(main_source.data["index"]))

    # Clear the source for knn figures
    for i in range(0, kNUM_SHOW):
        knn_fig_src = knn_figure_srcs[i]
        knn_fig_src.fig.title.text = "Top " + str(i+1) + " NN"

        for src in knn_fig_src.srcs:
            src.data['index'] = []
            src.data['close'] = []

    #Clear the source for predict figures

    for src in predict_figure_src.srcs:
        src.data['index'] = []
        src.data['close'] = []

def main():
    '''Main program to execute when server starts up

    Steps:
        * Create figures, widgets, redis source and knn-predictor and make them global
        * Arrange the figures and plot
        * Populate data for graph to display
    '''

    global option_dropdown
    global main_figure_src
    global knn_figure_srcs
    global predict_figure_src
    global knn_predictor
    global redis_source

    redis_source = redis_io.RedisSource()
    knn_predictor = knn.KnnGaussianPrediction()

    option_dropdown = CreateDropdown(redis_source.options())
    option_dropdown.on_click(ChangeSource)

    predict_button = Button(label="Predict!", button_type="warning")
    predict_button.on_click(Predict)

    main_figure_src = CreateMainFigure()
    knn_figure_srcs = CreateKnnFigures()
    predict_figure_src = CreatePredictFigure()


    #Organize the plot
    pred_plot = column(widgetbox(option_dropdown, predict_button), predict_figure_src.fig)
    main_plot = row(main_figure_src.fig, pred_plot)
    knn_figures = [fs.fig for fs in knn_figure_srcs]
    knn_plot = row(knn_figures)
    plot = column(main_plot, knn_plot)
    curdoc().add_root(plot)

    #Populate the graph data
    ChangeSource(option_dropdown.default_value)

main()
