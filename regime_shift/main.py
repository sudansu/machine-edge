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



def CreateMainSource(option):
    _df = sources.GetDataFrame(option)
    # print ("Creating Main Source: ")
    # print ("Type _dt.index")
    # print (type(_df.index))
    colors = ["navy"] * len(_df.index)
    probs = ["N.A."] * len(_df.index)
    sizes = [2] * len(_df.index)


    circle_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors,size = sizes,prob = probs))

    idx_line = []
    close_line = []
    colors_line = []
    for i  in range(len(_df.index) - 1):
        idx_line.append([_df.index[i], _df.index[i+1]])
        close_line.append([_df.close[i], _df.close[i+1]])
        colors_line.append("navy")

    line_source = ColumnDataSource(data=dict(index=idx_line, close=close_line, color=colors_line))
    return circle_source, line_source



def CreateMainFigure():
    _tools = "pan,box_zoom,wheel_zoom, reset"
    _fig = figure(width=800, height=350, x_axis_type="datetime", tools=_tools, webgl=True)
    # _fig.line('index', 'close', source=main_source, line_color='navy', line_alpha=1, legend='daily-close')


    _fig.multi_line('index', 'close', source=line_source, color='color', line_width=1, line_alpha=1, legend='daily-close')


    # _fig.multi_line(idx_line, close_line, color=colors, line_width=1)
    # _fig.line('index', 'close', source=main_source, line_color='red', line_alpha=1, legend='daily-close')
    _line_renderer = _fig.circle('index', 'close', source=main_source, color='color', size='size', legend='daily-close')

    # customize figure by setting attributes
    _fig.title.text = dropdown.default_value + " (daily)"
    _fig.title.align = "center"
    _fig.legend.location = "top_left"
    _fig.grid.grid_line_alpha=0
    _fig.xaxis.axis_label = 'Date'
    _fig.yaxis.axis_label = 'Price'
    _fig.ygrid.band_fill_color="olive"
    _fig.ygrid.band_fill_alpha=0.1

    hover = HoverTool(renderers=[_line_renderer],point_policy = "follow_mouse",tooltips=[
        ("Price", "@close"),
        ("Turbulance Prob", "@prob"),
    ])
    _fig.add_tools(hover)

    # hover = _fig.select_one(HoverTool)
    # hover.point_policy = "follow_mouse"
    # hover.tooltips = 
    analyze()
    return _fig

def ChangeRange(new):
    range_dropdown.label = new
    option = dropdown.default_value

    if new == "reset":
        ChangeSource(option)
        return

    # _df = sources.GetDataFrame(option)
    pre_days = int(re.findall(r'\d+', new)[0])
    # print(pre_days)

    # all_circle_source,all_line_source = CreateMainSource(option)
    # analyze()

    circle_index = all_circle_data['index'][-pre_days:]
    circle_close = all_circle_data['close'][-pre_days:]
    circle_color = all_circle_data['color'][-pre_days:]
    circle_size = all_circle_data['size'][-pre_days:]
    circle_prob = all_circle_data['prob'][-pre_days:]

    line_index = all_line_data['index'][-pre_days+1:]
    line_close = all_line_data['close'][-pre_days+1:]
    line_color = all_line_data['color'][-pre_days+1:]

    main_source.data = dict(index=circle_index, close=circle_close, color=circle_color, size=circle_size,prob=circle_prob)
    line_source.data = dict(index=line_index, close=line_close, color=line_color)

    # #Perform Regime Analysis
    # ri.SetSource(list(_df.close[-pre_days:]))
    # turb_probs = ri.predict_prob()
    # #print(turb_prob)

    # turb_threshold = 0.75

    # colors = []
    # sizes = []
    # for prob in turb_probs:
    #     if prob > turb_threshold:
    #         colors.append("red")
    #         sizes.append(5)
    #     else:
    #         colors.append("navy")
    #         sizes.append(2)

    # _new_source = ColumnDataSource(data=dict(index=_df.index[-pre_days:], close=_df.close[-pre_days:],color=colors,size = sizes,prob=turb_probs))
    # main_source.data = _new_source.data




def ChangeSource(new):
    global all_circle_data
    global all_line_data
    main_fig.title.text = new + " (daily)"
    dropdown.label = new
    range_dropdown.label="Range"
    new_circle_source,new_line_source = CreateMainSource(new)

    # _df = sources.GetDataFrame(new)
    # colors = ["navy"] * len(_df.index)

    # probs = ["N.A."] * len(_df.index)
    # sizes = [2] * len(_df.index)
    # _new_source = ColumnDataSource(data=dict(index=_df.index, close=_df.close,color=colors,size=sizes,prob = probs))




    main_source.data = new_circle_source.data
    line_source.data = new_line_source.data
    ri.SetSource(main_source.data['close'])
    analyze()
    all_circle_data = dict(main_source.data)
    all_line_data = dict(line_source.data)


def analyze():

    length = len(main_source.data['index'])
    colors = ["navy"] * length
    turb_probs = ri.predict_prob()
    turb_threshold = 0.9
    for i, turb_prob in enumerate(turb_probs):
        if turb_prob > turb_threshold:
            colors[i] = "red"
    main_source.data['color'] = colors
    main_source.data['prob'] = turb_probs

    line_colors = ["navy"] * (length - 1)

    # print ("length - 1", length - 1)
    # print ("len of line source index: ", len(line_source.data['index']))

    for i in range(len(turb_probs) - 1):
        if turb_probs[i] > turb_threshold and turb_probs[i+1] > turb_threshold:
            line_colors[i] = "red"  
    line_source.data['color'] = line_colors
 
    # print(is_turbulant)
    # print("Turbulance Length: ", len(is_turbulant))
    # print("Source Length: ", length)


# get data sources
sources = DataSource()

# add widgets
dropdown = CreateDropdown()
# get main source
main_source,line_source = CreateMainSource(dropdown.default_value)

#Create Regime Identifier
ri = RegimeIdentifier()
ri.SetSource(main_source.data['close'])

# draw main figure
main_fig = CreateMainFigure()
# add dropdown on click actions

all_circle_data = dict(main_source.data)
all_line_data = dict(line_source.data)

dropdown.on_click(ChangeSource)
range_dropdown = CreateRangeDropDown()

range_dropdown.on_click(ChangeRange)
# add button for prediction
# button = Button(label="Analyze!", button_type="warning")
# button.on_click(analyze)

main_plot = row(main_fig, widgetbox(dropdown, range_dropdown))
curdoc().add_root(main_plot)
