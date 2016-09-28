# machine-edge
A modern approach to trading visualization and prediction

## Redis
Redis is used as in-memory data store. You can either interact with Reids from command-line using 'redis-cli' or GUI Redis Desktop Manager. Reids supports persistence. 
* The database saves to disk periodically: /var/lib/redis/dump.rdb
* The config file for redis: /etc/redis/redis.conf

## Real-time market data
I have a subscription to Bloomberg where I get historical time-series and real-time market data. However, there is only Windows API. Currently, I extract these data and save them to Redis on Windows machine. Then transfer the 'dump.rdb' to Linux.

There is a Linux API, but it requires corporate subscription. We will talk about this after the prototype stage.

## HP laptop
I have set up Ubuntu 16.04 LTS. I have installed the latest libraries:

#### Python
Please use 'python3' and 'pip3'. Ubuntu has dependencies on Python 2.x, but for this project, we will only use the latest versions.

#### ipython
This is a much better shell for Python. Just type 'ipython' from terminal.

#### jupyter notebook
Even better than ipython. Type 'jupyter notebook' from terminal.

## Visualization
For the prototype, let's use [Bokeh](http://bokeh.pydata.org/en/latest/). We can bypass JavaScript completely. We will revisit and think d3.js for future development.

## Prediction/Machine-learning
For the prototype, we can use [scikit-learn](http://scikit-learn.org/stable/)

## For cleaning data / data structure
Let's use [pandas](http://pandas.pydata.org/)
