import numpy as np

import yaml

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure

from bokeh.io import show, output_file, output_notebook, push_notebook
from bokeh.models import ColumnDataSource
from bokeh.themes import Theme
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, LogTicker, ColorBar, RadioButtonGroup, CustomJS, Slider
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, Circle, HoverTool, CustomJS
from bokeh.plotting import figure
import datetime
import calendar

import numpy as np
import pandas as pd

# splits df into split buckets and returns list of smaller dfs
def splitTime(source, split):

    #source.sort_values(by=['timenums'])
    z = source['timenums'].tolist()
    z.sort()

    minNum = min(z)
    maxNum = max(z)

    rangeNum = maxNum - minNum
    print(rangeNum)
    splitNum = rangeNum/split

    newDF = []
    newDF.append(minNum)

    for i in range(split):
        minNum += splitNum
        newDF.append(minNum)
        
    print(newDF)
    
    return newDF

# convert numbers back to time for pretty display
def pretty_time(time):
    return datetime.fromtimestamp(time).strftime("%A, %B %d, %Y %I:%M:%S")

def miniPlot(source):

    # Shamelessly stolen from bokeh doccumentation
    # https://docs.bokeh.org/en/0.10.0/docs/user_guide/interaction.html#userguide-interaction-actions-widget-callbacks
    # some minor additions to work with our data

    dayDensity = []
    dayTime = []
    #source.sort_values(by=['timenums'])
    z = source['timenums'].tolist()
    z.sort()
    print("length of z = ", len(z))

    minNum = min(z)//(3600*24)
    maxNum = max(z)//(3600*24)
    rangeDays = maxNum - minNum
    print("rangeDays =", rangeDays)

    j = 0
    count = 0
    for i in range(rangeDays):
        print("new day location = ", minNum + i)
        while((z[j]//(3600*24) == minNum+i)):
            count +=1
            j +=1
        dayDensity.append(count)
        count = 0
        dayTime.append(z[j])

    #d = {'density': hourDensity, 'time': hourTime}
    #newDF = pd.DataFrame(data=d)

    print("length of dayDensity = ", len(dayDensity))
    print(dayDensity)
    print("length of dayTime = ", len(dayTime))
    print(dayTime)

    (x,y) = (dayTime, dayDensity)

    p = figure(width=1000, height=400, tools="", toolbar_location=None, title='Tweet Density Per Day', sizing_mode="scale_width")
    p.line(x, y, line_dash="4 4", line_width=1, color='gray')

    # Add a circle, that is visible only when selected
    source = ColumnDataSource({'x': x, 'y': y})
    invisible_circle = Circle(x='x', y='y', fill_color='gray', fill_alpha=0.05, line_color=None, size=20)
    visible_circle = Circle(x='x', y='y', fill_color='firebrick', fill_alpha=0.5, line_color=None, size=20)
    cr = p.add_glyph(source, invisible_circle, selection_glyph=visible_circle, nonselection_glyph=invisible_circle)

    # Add a hover tool, that selects the circle
    code = "source.set('selected', cb_data['index']);"
    callback = CustomJS(args={'source': source}, code=code)
    p.add_tools(HoverTool(tooltips=None, callback=callback, renderers=[cr], mode='hline'))

    return p

