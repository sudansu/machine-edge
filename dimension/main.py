from datasource import DataSource
from dimension_reduction import Dim_Red
from sklearn.cluster import AgglomerativeClustering


sources = DataSource()
dim_red = Dim_Red()
options = sources.Options()

result = sources.GetAllDataFrame(10)
print ("Finish Getting Data Frames")

src = [list(r.close) for r in result]

# for s in src:
# 	print ("len: ", len(s))
# print(src)
dim_red.SetSource(options, src)

# print ("Rate: ")
# for r in dim_red._source:
# 	print(type(r))
# 	print(r)


# print(dim_red.GetDistMatrix())
dists = dim_red.GetDistMatrix()
labels = dim_red.GetClusters(dists,4)
dim_red.GetRepre(dists, labels,4)