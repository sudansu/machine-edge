class FigureSource(object):
    '''
    a class that encapsulates the bokeh figure and data source in figure
    '''

    def __init__(self, bokeh_fig):
        self.fig = bokeh_fig
        self.srcs = []

    def add_source(self, src):
        self.srcs.append(src)

    def add_sources(self, srcs):
        self.srcs.extend(srcs)
