from bokeh.plotting import figure, curdoc
from bokeh.models import HoverTool

from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import Dropdown, Button
import re
from datasource import DataSource
from regime import RegimeIdentifier
# from prediction import KnnPrediction

def CreateDropdown():
    _options = sources.Options()
    _menu = list(zip(_options, _options))
    return Dropdown(label=_options[0], button_type="success", menu=_menu, default_value=_options[0])

def CreateRangeDropDown():
    ranges = [30,60,90]
    labels = ["Recent %d Days" % r for r in ranges ]

    _menu = list(zip(labels, labels))
    _menu.append(("reset","reset"))
    return Dropdown(label="Range", button_type="success", menu=_menu, default_value=labels[0])



def CreateMainSource():
    _df = sources.GetDataFrame(dropdown.default_value)
    # print ("Creating Main Source: ")
    # print ("Type _dt.index")
    # print (type(_df.index))
    colors = ["navy"] * len(_df.index)
    probs = ["N.A."] * len(_df.index)
    sizes = [2] * len(_df.index)

    return ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors,size = sizes,prob = probs))

def CreateMainFigure():
    _tools = "pan,box_zoom,wheel_zoom,hover, reset"
    _fig = figure(width=800, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    _fig.line('index', 'close', source=main_source, color='blue', line_alpha=1, legend='daily-close')
    _renderer = _fig.circle('index', 'close', source=main_source, color='color', size='size', legend='daily-close')

    # customize figure by setting attributes
    _fig.title.text = dropdown.default_value + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha=0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1

    hover = _fig.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = [
        ("Price", "@close"),
        ("Turbulance Prob", "@prob"),
    ]
    return _fig

def ChangeRange(new):
    range_dropdown.label = new
    option = dropdown.default_value

    if new == "reset":
        ChangeSource(option)
        return

    _df = sources.GetDataFrame(option)
    pre_days = int(re.findall(r'\d+', new)[0])
    # print(pre_days)


    #Perform Regime Analysis
    ri.SetSource(list(_df.close[-pre_days:]))
    turb_probs = ri.predict_prob()
    #print(turb_prob)

    turb_threshold = 0.75

    colors = []
    sizes = []
    for prob in turb_probs:
        if prob > turb_threshold:
            colors.append("red")
            sizes.append(5)
        else:
            colors.append("navy")
            sizes.append(2)

    _new_source = ColumnDataSource(data=dict(index=_df.index[-pre_days:], close=_df.close[-pre_days:],color=colors,size = sizes,prob=turb_probs))
    main_source.data = _new_source.data




def ChangeSource(new):
    main_fig.title.text = new + " (daily)"
    dropdown.label = new
    _df = sources.GetDataFrame(new)
    colors = ["navy"] * len(_df.index)

    probs = ["N.A."] * len(_df.index)
    sizes = [2] * len(_df.index)
    _new_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors,size=sizes,prob = probs))
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
range_dropdown = CreateRangeDropDown()

range_dropdown.on_click(ChangeRange)
# add button for prediction
# button = Button(label="Analyze!", button_type="warning")
# button.on_click(analyze)

main_plot = row(main_fig, widgetbox(dropdown, range_dropdown))
curdoc().add_root(main_plot)
