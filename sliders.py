''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
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
import miniVis

import numpy as np
import pandas as pd

df = pd.read_csv("natural_disaster_human_mobility.csv", error_bad_lines = False)
"""
# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))


# Set up plot
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)


# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)


# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4*np.pi, N)
    y = a*np.sin(k*x + w) + b

    source.data = dict(x=x, y=y)

for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(text, offset, amplitude, phase, freq)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"
"""

#convert time to numbers and add to df
timenums = []
for time in df['time']: 
    
    date = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    date = calendar.timegm(date.utctimetuple())
    timenums.append(date)
   
df['timenums'] = timenums

# convert numbers back to time for pretty display
def pretty_time(time):
    return datetime.fromtimestamp(time).strftime("%A, %B %d, %Y %I:%M:%S")

#def data_viz(doc): 

    
#initial dataset
gdf = df[df['disaster.event'] == '33_Baltimore'][['latitude', 'longitude.anon', 'timenums']]
#smalData = miniVis.splitTime(gdf, 3)
#gdf = smalData[0]

#.sample(n = 10000)

source = ColumnDataSource(data = gdf)
    
#color coding
color_mapper = LinearColorMapper(palette = 'Magma256', low = min(source.data['timenums']), high=max(source.data['timenums']))
color_bar = ColorBar(color_mapper = color_mapper, ticker = LogTicker(),
                label_standoff = 12, border_line_color = None, location = (0,0))
#plot
TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
p = figure(plot_width = 1000, plot_height = 1000, tools = TOOLS, sizing_mode="scale_width")
r = p.scatter(x = 'longitude.anon', y = 'latitude', source = source, color = {'field': 'timenums', 'transform': color_mapper})
p.add_layout(color_bar, 'right')

q = miniVis.miniPlot(gdf)

#add radio buttons
def disasterUpdate(new): 
        
    update(new, time_button_group.active)


def timeUpdate(new):

    update(radio_button_group.active, new)

def update(disaster, time): 

    gdf = df[df['disaster.event'] == df['disaster.event'].unique()[radio_button_group.active]][['latitude','longitude.anon', 'timenums']]

    if(time_button_group.active > 0): 

        time = time_button_group.active
        times = miniVis.splitTime(gdf, 10)
        gdf = gdf[(gdf['timenums'] > times[time - 1]) & (gdf['timenums'] < times[time])]

    print(gdf)
    source = ColumnDataSource(data = gdf)
    r.data_source.data = source.data
    
    color_mapper.low = min(r.data_source.data['timenums'])
    color_mapper.high = max(r.data_source.data['timenums']) 
    
    q = miniVis.miniPlot(source)

    
radio_button_group = RadioButtonGroup(labels = [i for i in df['disaster.event'].unique()], active = 12)
radio_button_group.on_click(disasterUpdate)

time_button_group = RadioButtonGroup(labels = [str(i) for i in range(0,11)], active = 0)
time_button_group.on_click(timeUpdate)

#add slider
#def callback(attr, old, new):
    
    #gdf = df[df['disaster.event'] == df['disaster.event'].unique()[radio_button_group.active]][['latitude','longitude.anon', 'timenums']]
    #smalData = miniVis.splitTime(gdf, 3)
    #gdf = smalData[0]
    #source.data = ColumnDataSource(data = gdf[gdf['timenums'] < new]).data

#slider = Slider(start=min(gdf.timenums), end=max(gdf.timenums), value=max(gdf.timenums), step=50000, title="time")
#slider.on_change('value', callback)
  
curdoc().add_root(column(radio_button_group, time_button_group, p, q, sizing_mode="scale_width"))
curdoc().theme = 'light_minimal'