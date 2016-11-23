from datasource import DataSource
from dimension_reduction import Dim_Red
from sklearn.cluster import AgglomerativeClustering



from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, row, column, widgetbox
# from bokeh.models import Circle, ColumnDataSource, BoxSelectTool
# from bokeh.models.widgets import Dropdown, Button

from bokeh.models.widgets import Slider, Button
# from bokeh.io import output_file, show, vform


def create_range_slider():
	return Slider(start=0, end=120, value=90, step=1, title="Latest Date")

def create_cluster_slider(max_cluster_count):

	return Slider(start=1,end=max_cluster_count, value=4,step=1, title="Number of Representatives"  )


def Analyze():
	global sources,src,dim_red

	cluster_count = cluster_slider.value
	latest_points = range_slider.value

	# print("Cluster: ", cluster_count, " Latest Points: ", latest_points)	
	data = sources.GetAllDataFrame(latest_points)

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
	labels = dim_red.GetClusters(dists,4)
	repre = dim_red.GetRepre(dists, labels,4)
	# print("Labels: ", labels)
	# print("Repre: ", repre)

	return 

sources = DataSource()
dim_red = Dim_Red()
options = sources.Options()
dim_red.SetOptions(options)

range_slider = create_range_slider()
cluster_slider = create_cluster_slider(len(options))
button = Button(label="Analyze!", button_type="warning")
button.on_click(Analyze)
plot = column(widgetbox(range_slider, cluster_slider, button))

curdoc().add_root(plot)
