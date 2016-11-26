from datasource import DataSource
from dimension_reduction import Dim_Red
from sklearn.cluster import AgglomerativeClustering


from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
# from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
# from bokeh.models.widgets import Dropdown, Button

from bokeh.models.widgets import Slider, Button,PreText
# from bokeh.io import output_file, show, vform

def create_figure_from_option(data_source, option, pre_days):
	df = data_source.GetDataFrame(option)
	index = df.index[-pre_days:]
	close = df.close[-pre_days:]

	return create_figure_from_source(option, index, close)

def create_figure_from_source(option, index, close):

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
	_fig.grid.grid_line_alpha=0
	_fig.xaxis.axis_label = 'Date'
	_fig.yaxis.axis_label = 'Price'
	_fig.ygrid.band_fill_color="olive"
	_fig.ygrid.band_fill_alpha=0.1
	return _fig

def create_range_slider():
	return Slider(start=0, end=120, value=90, step=1, title="Latest Date")

def create_cluster_slider(max_cluster_count):

	return Slider(start=1,end=max_cluster_count, value=4,step=1, title="Number of Clusters"  )


def Analyze():
	global sources,src,dim_red
	#Remove existing figures
	container = curdoc().get_model_by_name("container")
	figs_col = curdoc().get_model_by_name("figs")

	if figs_col is not None:
		container.children.remove(figs_col)

	cluster_count = cluster_slider.value
	latest_points = range_slider.value

	# print("Cluster: ", cluster_count, " Latest Points: ", latest_points)	
	data = sources.GetAllDataFrame(latest_points)

	print("Finish getting data...")
	src = [list(r.close) for r in data]

	# for s in src:
	# 	print ("len: ", len(s))
	# print(src)
	dim_red.SetSource(src)

	# print ("Rate: ")
	# for r in dim_red._source:
	# 	print(type(r))
	# 	print(r)


	# print(dim_red.GetDistMatrix())
	dists = dim_red.GetDistMatrix()


	# for dist in dists:
	# 	for d in dist:
	# 		print(str(d), end="\t")
	# 	print("\n",end="")


	# for i, opt in enumerate(sources.Options()):
	# 	print(str(i+1), "\t", opt)

	labels = dim_red.GetClusters(dists,cluster_count)
	cluster_repres = dim_red.GetRepre(dists, labels,cluster_count)
	# print("Labels: ", labels)
	# print("Repre: ", cluster_repres)


	#Append the figure
	# fig_col = column()
	# fig = create_figure_from_option(sources, options[1], 90)

	# fig_col = column([fig], name="figs")
	print("Start Plotting...")
	cluster_rows = []
	for repre, cluster in cluster_repres.items():
		# print("repre: ", repre)
		# print("cluster: ", cluster)
		cluster_figs = []

		repre_option = sources.Options()[repre]
		cluster_figs.append(create_figure_from_option(sources,repre_option,latest_points))

		for optionID in cluster:
			option = sources.Options()[optionID]
			cluster_figs.append(create_figure_from_option(sources,option,latest_points))

		cluster_rows.append(row(cluster_figs))
	fig_col = column(cluster_rows, name="figs")

	container.children.append(fig_col)
	print("Finish Plotting...")
	return 

sources = DataSource()
dim_red = Dim_Red()
options = sources.Options()
dim_red.SetOptions(options)

range_slider = create_range_slider()
cluster_slider = create_cluster_slider(len(options))
button = Button(label="Analyze!", button_type="warning")
button.on_click(Analyze)

# pre = PreText(text="Each cluster in one row. The first column in thr row for cluster representatives",width=500, height=100)



fig = create_figure_from_option(sources, options[0], 90)

control_row = row([range_slider, cluster_slider, button],name="control")

# figs_col = column([fig], name="figs")
fig_container = column([], name="container")

plot = column([control_row, fig_container])

curdoc().add_root(plot)
