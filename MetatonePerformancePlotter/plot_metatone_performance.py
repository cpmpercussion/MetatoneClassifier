import numpy as np
import pandas as pd
import transitions
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from datetime import timedelta
from ggplot import *
import time

#
directory_path = '/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/'
performance_name = '2014-03-17T18-30-57-MetatoneOSCLog'
#
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/'
# performance_name = '2014-03-17T18-09-46-MetatoneOSCLog'
#
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/'
# performance_name = '2014-03-17T17-40-14-MetatoneOSCLog'

#
# Setup
#
performance_time = time.strptime(performance_name[:19],'%Y-%m-%dT%H-%M-%S')
plot_title = "Metatone " + time.strftime('%y-%m-%d %H:%M',performance_time)

events_path = directory_path + performance_name + '-events.csv'
gestures_path = directory_path + performance_name + '-gestures.csv'
metatone_path = directory_path + performance_name + '-metatone.csv'
online_path = directory_path + performance_name + '-online.csv'
touches_path = directory_path + performance_name + '-touches.csv'
transitions_path = directory_path + performance_name + '-transitions.csv'

events = pd.read_csv(events_path, index_col='time', parse_dates=True)
gestures = pd.read_csv(gestures_path, index_col='time', parse_dates=True)
metatone = pd.read_csv(metatone_path, index_col='time', parse_dates=True)
online = pd.read_csv(online_path, index_col='time', parse_dates=True)
touches = pd.read_csv(touches_path, index_col='time', parse_dates=True)
transitions_frame = pd.read_csv(transitions_path, index_col='time', parse_dates=True)

transition_states = {
    'stasis':0,
    'convergence':1,
    'divergence':2,
    'development':3}

#TODO use the players in the performance...
# performers = touches['device_id'].unique()

#TODO - some kind of "activity" plot like....
#activity = touches['device_id'].resample('S', how='count')

def plot_gesture_score_and_transitions():
    transitions_to_plot = transitions_frame.apply(lambda s: [transition_states[s[0]],s[1],s[2]], axis=1)
    new_ideas = events.index

    #Gesture Score:
    idx = gestures.index
    ax = plt.figure(figsize=(25,10),frameon=False,tight_layout=True).add_subplot(311)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    plt.title(plot_title)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(),gestures[n],'-',label=n)
    plt.legend(loc='upper right')

    # Transition Type
    ax2 = plt.subplot(312, sharex=ax)
    ax2.xaxis.grid(True,which="major")
    ax2.yaxis.grid()
    idx = transitions_to_plot.index
    plt.plot_date(idx.to_pydatetime(),transitions_to_plot['transition_type'],'-',label='transition_type')
    plt.ylabel("transition type")
    plt.ylim(-0.25,3.25)
    plt.yticks(np.arange(4),['sta','con','div','dev'])

    ## Transition Parameters
    ax3 = plt.subplot(313, sharex=ax)
    ax3.xaxis.grid(True,which="major")
    ax3.yaxis.grid()
    plt.plot_date(idx.to_pydatetime(),transitions_to_plot['spread'],'-',label='spread')
    plt.plot_date(idx.to_pydatetime(),transitions_to_plot['ratio'],'-',label='ratio')
    plt.ylim(-0.1,1.1)
    plt.legend(loc='upper right')
    plt.ylabel("transition params")

    ## Plot Lines for each event.
    for n in range(len(new_ideas)):
        x_val = new_ideas[n].to_pydatetime()
        ax.axvline(x=x_val, color='black')
        ax2.axvline(x=x_val, color='black')
        ax3.axvline(x=x_val, color='black')
    plt.savefig(plot_title.replace(":","_") + '.png', dpi=150, format="png")
    plt.close()


def plot_score_and_changeyness(gestures_frame,window,threshold):
    window_seconds = window #15
    winlen = str(window_seconds) + "s"
    new_idea_difference_threshold = threshold #0.15
    
    group_trans = transitions.calculate_group_transitions_for_window(gestures_frame,'15s')
    transition_activity = transitions.calculate_transition_activity_for_window(gestures_frame,winlen)
    new_ideas = transitions.calculate_new_ideas(transition_activity, new_idea_difference_threshold)    
	
    #Plot and save the Gesture Score as a png:
    idx = gestures_frame.index
    ax = plt.figure(figsize=(25,10),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    title = "Gesture Score and Transitions " + transition_activity.index[0].isoformat() + " " + str(len(new_ideas)) + " new ideas with threshold " + str(new_idea_difference_threshold)
    plt.title(title)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures_frame.columns:
        plt.plot_date(idx.to_pydatetime(),gestures_frame[n],'-',label=n)
    plt.legend(loc='upper right')
    
    transition_activity = transition_activity.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    idx = transition_activity.index
    plt.plot_date(idx.to_pydatetime(),transition_activity,'-',label=transition_activity.name)
    plt.ylabel("changeyness")
    
    for n in range(len(new_ideas)):
        x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window_seconds / 2)
        ax.axvline(x=x_val, color='r')
        ax2.axvline(x=x_val, color='r')
        print x_val
    
    #plt.xlabel("time")
    plt.savefig(title.replace(":","_") + " " + winlen + '.png', dpi=150, format="png")
    plt.close()

# Testing ggplot
def testing_ggplot():
    gestures['date'] = gestures.index
    #gestures_lng = pd.melt(gestures, id_vars=['date'], var_name="performer", value_name="gesture")
    gestures_lng = pd.melt(gestures, id_vars=['date'])
    gestures_lng.columns = ['date','performer','gesture']
    ggplot(aes(x='date', y='gesture', colour='performer'), data=gestures_lng) + geom_line() + ggtitle(plot_title) + scale_x_date(breaks=dates.SecondLocator(bysecond=[0]),labels="%H:%M:%S")

