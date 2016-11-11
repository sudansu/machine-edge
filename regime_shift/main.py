from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button

from datasource import DataSource
from regime import RegimeIdentifier
# from prediction import KnnPrediction

def CreateDropdown():
    _options = sources.Options()
    _menu = list(zip(_options, _options))
    return Dropdown(label=_options[0], button_type="success", menu=_menu, default_value=_options[0])

def CreateMainSource():
    _df = sources.GetDataFrame(dropdown.default_value)
    # print ("Creating Main Source: ")
    # print ("Type _dt.index")
    # print (type(_df.index))

    colors = ["navy"] * len(_df.index)
    return ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors))

def CreateMainFigure():
    _tools = "pan,box_zoom,wheel_zoom,reset"
    _fig = figure(width=800, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    _fig.line('index', 'close', source=main_source, color='blue', line_alpha=1, legend='daily-close')
    _renderer = _fig.circle('index', 'close', source=main_source, color='color', size=2, legend='daily-close')

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



def ChangeSource(new):
    main_fig.title.text = new + " (daily)"
    dropdown.label = new
    _df = sources.GetDataFrame(new)
    colors = ["navy"] * len(_df.index)
    _new_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors))
    main_source.data = _new_source.data
    ri.SetSource(main_source.data['close'])


def analyze():

    length = len(main_source.data['index'])
    colors = ["navy"] * length
    is_turbulant = ri.predict()
    for i, is_turb in enumerate(is_turbulant):
        if is_turb:
            colors[i] = "red"
    main_source.data['color'] = colors
    # print(is_turbulant)
    # print("Turbulance Length: ", len(is_turbulant))
    # print("Source Length: ", length)


# get data sources
sources = DataSource()

# add widgets
dropdown = CreateDropdown()
# get main source
main_source = CreateMainSource()

#Create Regime Identifier
ri = RegimeIdentifier()
ri.SetSource(main_source.data['close'])

# draw main figure
main_fig = CreateMainFigure()
# add dropdown on click actions
dropdown.on_click(ChangeSource)
# add button for prediction
button = Button(label="Analyze!", button_type="warning")
button.on_click(analyze)

main_plot = row(main_fig, widgetbox(dropdown, button))
curdoc().add_root(main_plot)
