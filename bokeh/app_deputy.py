from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import Slider, Button,PreText
from bokeh.layouts import gridplot, row, column, widgetbox

from sklearn.cluster import AgglomerativeClustering

from source import redis_io
from core import deputy

figure_srcs_dict = {} #a dict that maps option to its figure
redis_src = None
repre_analyzer = None
cluster_slider = None
range_slider = None

def CreateFigForSource(redis_src, option, pre_days):
    '''
        create figure for currency option
        Args:
            redis_src: a RedisSource instance that provide data
            option: the currecy for plotting, e.g, sgd, aud ...
            pre_days: the number of the most recent days to consider for finding representative

        Returns:
            a bokeh figure
    '''

    df = redis_src.data_frame(option, -pre_days)
    index = df.index[-pre_days:]
    close = df.close[-pre_days:]

    data_source = ColumnDataSource(data=dict(index=index, close=close))
    # data_source = ColumnDataSource(data=dict())
    _tools = "pan,wheel_zoom,reset"
    _fig = figure(width=400, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    _fig.line('index', 'close', source=data_source, color='navy', line_alpha=0.5, legend='daily-close')
    _renderer = _fig.circle('index', 'close', source=data_source, color='navy', size=2, legend='daily-close')
    # set select/unselect color

    # customize figure by setting attributes
    _fig.title.text = option + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha = 0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color = "olive"
    _fig.ygrid.band_fill_alpha = 0.1

    return _fig

def Analyze():
    '''Function to be triggered when clicking the analyze buttion

        Several steps are to be done:
            * remove previous figures
            * Update figure data  based on selected most recent days
            * Compute clusters and representatives
            * Reorganize the figures for plotting based on cluster
    '''

    global repre_analyzer
    global redis_src
    global cluster_slider
    global range_slider

    #Remove existing figures
    container = curdoc().get_model_by_name("container")
    figs_col = curdoc().get_model_by_name("figs")

    if figs_col is not None:
        container.children.remove(figs_col)

    cluster_count = cluster_slider.value
    pre_points = range_slider.value

    all_dfs = redis_src.all_data_frames(start_point=-pre_points)
    for df in all_dfs:
        repre_data.append(list(df.close))

    repre_analyzer.fit(repre_data)
    cluster_labels = repre_analyzer.cluster(cluster_count)#cluster label for each source

    cluster_repres = {}
    #cluster_repres maps cluster reprentative currency index to a list of other currency indice in this cluster
    for option_id, cluster_id in enumerate(cluster_labels):
        repre_id = repre_analyzer.find_representative(cluster_id)
        if repre_id not in cluster_repres:
            cluster_repres[repre_id] = []

        if  option_id != repre_id:
            cluster_repres[repre_id].append(option_id)

    # print('cluster repres: ', cluster_repres)

    #Reorganize the figure plotting
    #figures in a row are within one cluster
    #1st fig in the row is cluster representative

    cluster_rows = []
    for repre, cluster in cluster_repres.items():
        # print("repre: ", repre)
        # print("cluster: ", cluster)
        cluster_figs = []

        repre_option = redis_src.options()[repre]
        

        # cluster_figs.append(figure_srcs_dict[repre_option].fig)
        cluster_figs.append(CreateFigForSource(redis_src, repre_option, pre_points))

        for optionID in cluster:
            option = redis_src.options()[optionID]
            cluster_figs.append(CreateFigForSource(redis_src, option, pre_points))

        cluster_rows.append(row(cluster_figs))
    fig_col = column(cluster_rows, name="figs")

    container.children.append(fig_col)
    print("Finish Plotting...")
    return 

def main():
    '''main program to execute when server starts up

        * Create redis source and dimnsion reduction engine
        * Create figures, widgets and set handlers
        * Organize the plot
    '''

    global redis_src
    global figure_srcs_dict
    global repre_analyzer
    global range_slider
    global cluster_slider

    redis_src = redis_io.RedisSource()
    repre_analyzer = deputy.RepresentativeSelection()
    range_slider = Slider(start=0, end=120, value=90, step=1, title="Latest Date")

    option_count = len(redis_src.options())
    cluster_slider = Slider(start=1,end=option_count, value=4,step=1, title="Number of Clusters"  )

    for option in redis_src.options():
        fs = CreateFigForSource(redis_src, option, range_slider.value)
        figure_srcs_dict[option] = fs

    button = Button(label="Analyze!", button_type="warning")
    button.on_click(Analyze)

    control_row = row([range_slider, cluster_slider, button],name="control")
    fig_container = column([], name="container")
    plot = column([control_row, fig_container])
    curdoc().add_root(plot)

main()

