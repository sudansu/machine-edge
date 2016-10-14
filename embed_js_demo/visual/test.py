import numpy as np

from bokeh.client import push_session
from bokeh.embed import components
from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot

def test_plot():
    # prepare some data
    N = 100
    x = np.linspace(0, 4*np.pi, N)
    y0 = np.sin(x)
    y1 = np.cos(x)
    y2 = np.sin(x) + np.cos(x)

    # create a new plot
    s1 = figure(width=250, plot_height=250, title=None)
    s1.circle(x, y0, size=10, color="navy", alpha=0.5)

    # NEW: create a new plot and share both ranges
    s2 = figure(width=250, height=250, x_range=s1.x_range, y_range=s1.y_range, title=None)
    s2.triangle(x, y1, size=10, color="firebrick", alpha=0.5)

    # NEW: create a new plot and share only one range
    s3 = figure(width=250, height=250, x_range=s1.x_range, title=None)
    s3.square(x, y2, size=10, color="olive", alpha=0.5)

    # NEW: put the subplots in a gridplot
    p = gridplot([[s1, s2, s3]], toolbar_location=None)

    return components(p)
