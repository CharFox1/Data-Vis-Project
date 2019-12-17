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

from bokeh.palettes import Spectral5
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.models import Legend, LegendItem

import datetime
import calendar
import os

from bokeh.palettes import brewer

import numpy as np
import pandas as pd

from geopy import distance

path = os.path.dirname(os.path.realpath(__file__))

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
    #print("length of z = ", len(z))

    minNum = min(z)//(3600)
    maxNum = max(z)//(3600)
    rangeDays = maxNum - minNum
    #print("rangeDays =", rangeDays)

    j = 0
    count = 0
    for i in range(rangeDays):
        #print("new day location = ", minNum + i)
        while((z[j]//(3600) == minNum+i)):
            count +=1
            j +=1
        dayDensity.append(count)
        count = 0
        dayTime.append(datetime.datetime.fromtimestamp(z[j]))

    #d = {'density': hourDensity, 'time': hourTime}
    #newDF = pd.DataFrame(data=d)

    #print("length of dayDensity = ", len(dayDensity))
    #print(dayDensity)
    #print("length of dayTime = ", len(dayTime))
    #print(dayTime)

    (x,y) = (dayTime, dayDensity)

    return (x,y)

def userDistances(source):
    # get total distance moved for each user
    # can take dataframe for all distasters, just one, or just one time bucket of one

    print("Starting to collect user distances")
    
    users = dict()
    distanceList = []
    count = 0

    print ("the length of the dataframe is ", source.shape[0])

    # loop through all users and make a list of all their locations
    for index, row in source.iterrows():
        if count % 10000 == 0:
            print(count)
        count +=1
        key = str(str(row['user.anon']) + "-" + str(row['disaster.event']))
        if key not in users:
            # lat and lon are backwards so switch them
            users[key] = [[(row['longitude.anon'], row['latitude']), row['disaster.event']]]
        else:
            users[key].append([(row['longitude.anon'], row['latitude']), row['disaster.event']])

    maxDist = 0

    for userKey in users.keys():
        distanceTraveled = 0
        locations = users[userKey]

        # need to make sure they have more than one location

        #print("locations[0] = ", locations[0])
        #print("len of locations = ", len(locations))

        # if they have 2 or more locations, their distance traveled can be measured
        if (len(locations) > 1) :
            for k in range(len(locations)-1):
                #print("about to compare ", locations[k][0], "and ", locations[k+1][0])
                distanceTraveled += distance.distance(locations[k][0], locations[k+1][0]).miles

            #print("adding user", userKey)
        
            # watch out for this monster... This is adding new rows on to the end
            # of the new dataframe called distances.  The third attribute is searching
            # through the source dataframe for the user in order to see what disaster
            # they were in.
            disaster = locations[0][1]
            distanceList.append([userKey, distanceTraveled, disaster])

            if (distanceTraveled > maxDist):
                maxDist = distanceTraveled
        
        # otherwise, distance traveled is 0  
        #else:
            #disaster = locations[0][1]
            #distanceTraveled = 0
            #distanceList.append([userKey, distanceTraveled, disaster])

    distances = pd.DataFrame(distanceList, columns = ['user', 'distance', 'disaster'])

    print("max dist = ", maxDist)

    return distances

def boxPlot(source):

    # Code for making the dataset for this vis, should exist already
    #userDist = userDistances(source)
    #print(userDist)
    #print("That was the user distances dataframe!")

    #pd.to_pickle(userDist, str(path)+"/userDistanceDataNo0s.pkl")
    #print("saved file")

    df = pd.read_pickle(str(path)+"/userDistanceDataNo0s.pkl")
    
    cats = ["Wipha", "Halong", "Kalmaegi", "Rammasun Manila", "Bohol", "Iquique", "Napa", "Norfolk", "Hamburg", "Atlanta", "Phoenix", "Detroit", "Baltimore", "Au Fire 1", "Au Fire 2"]
    colors = ["#118ab2", "#118ab2", "#118ab2", "#118ab2", "#06d6a0", "#06d6a0", "#06d6a0", "#efc3e6", "#efc3e6", "#efc3e6", "#ffd166", "#ffd166", "#ffd166", "#ef476f", "#ef476f"]
    disasterType = ["Typhoon", "Typhoon", "Typhoon", "Typhoon", "Earthquake", "Earthquake", "Earthquake", "Winter Storm", "Winter Storm", "Winter Storm", "Thunderstorm", "Thunderstorm", "Thunderstorm", "Wildfire", "Wildfire"]
    
    colorDict = dict(zip(cats, colors))

    lineColorHex = "#000000"
    backgroundColor = "#e8e8e8"
    midLineColor = "#c0c0c0"

    # find the quartiles and IQR for each category
    groups = df.groupby('disaster')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    # find the outliers for each category
    def outliers(group):
        cat = group.name
        return group[(group.distance > upper.loc[cat]['distance']) | (group.distance < lower.loc[cat]['distance'])]['distance']
    out = groups.apply(outliers).dropna()

    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = []
        outy = []
        for keys in out.index:
            outx.append(keys[0])
            outy.append(out.loc[keys[0]].loc[keys[1]])

    p = figure(tools="", background_fill_color=backgroundColor, x_range=cats, toolbar_location=None, sizing_mode="stretch_both")

    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.distance = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'distance']),upper.distance)]
    lower.distance = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'distance']),lower.distance)]

    # stems
    p.segment(cats, upper.distance, cats, q3.distance, line_color=lineColorHex)
    p.segment(cats, lower.distance, cats, q1.distance, line_color=lineColorHex)

    # boxes
    l = p.vbar(cats, 0.7, q2.distance, q3.distance, fill_color=colors, line_color=lineColorHex)
    p.vbar(cats, 0.7, q1.distance, q2.distance, fill_color=colors, line_color=lineColorHex)

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(cats, lower.distance, 0.2, 0.01, line_color=lineColorHex)
    p.rect(cats, upper.distance, 0.2, 0.01, line_color=lineColorHex)

    # outliers
    if not out.empty:
        p.circle(outx, outy, size=6, color="#ffffff", fill_alpha=0.6)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = midLineColor
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="12pt"
    p.xaxis.major_label_orientation = "vertical"
    p.title.text = "Non-zero Distance Traveled per Disaster Event"
    #legend = dict(zip(cats, disasterType))
    #p.add_layout(legend)
    #p.legend.location = "top_right"
    #p.legend.click_policy="mute"

    return p