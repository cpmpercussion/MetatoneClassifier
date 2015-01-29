#! /usr/bin/env python
#
# This script plots the data captured in Metatone Performances!
# Uses all 6 CSV files output during the performance.
#
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
import argparse

transition_states = {
    'stasis':0,
    'convergence':1,
    'divergence':2,
    'development':3}

#
#directory_path = '/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/'
#performance_name = '2014-03-17T18-30-57-MetatoneOSCLog'
#
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/'
# performance_name = '2014-03-17T18-09-46-MetatoneOSCLog'
#
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/'
# performance_name = '2014-03-17T17-40-14-MetatoneOSCLog'
#
# directory_path = '/Users/charles/Dropbox/Metatone/20140505/21-05-MetaLonsdale/'
# performance_name = '2014-05-05T21-05-37-MetatoneOSCLog'

# directory_path = '/Users/charles/Dropbox/Metatone/20140505/21-12-BirdsNest/'
# performance_name = '2014-05-05T21-12-48-MetatoneOSCLog'
# directory_path = '/Users/charles/Dropbox/Metatone/20140505/20-39-StudyInBowls/'
# performance_name = '2014-05-05T20-39-43-MetatoneOSCLog'

# directory_path = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/MetatoneAgentGen/testLog2014-07-04/'
# performance_name = '2014-07-04T15-57-04-MetatoneOSCLog'

# directory_path = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/MetatoneAgentGen/logs/'
# performance_name = '2014-07-07T15-06-02-MetatoneOSCLog'

# input_filename = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/MetatoneAgentGen/logs/2014-07-07T15-06-02-MetatoneOSCLog.log'


def plot_gesture_score_and_transitions(plot_title,events,gestures,metatone,online,touches,transitions_frame):
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
        ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax2.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax3.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
    plt.savefig(plot_title.replace(":","_") + '.pdf', dpi=150, format="pdf")
    plt.close()

def plot_gesture_score(plot_title,events,gestures,metatone,online,touches,transitions_frame):
    transitions_to_plot = transitions_frame.apply(lambda s: [transition_states[s[0]],s[1],s[2]], axis=1)
    new_ideas = events.index

    #Gesture Score:
    idx = gestures.index
    ax = plt.figure(figsize=(35,10),frameon=False,tight_layout=True).add_subplot(111)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    # plt.title(plot_title)
    # plt.ylabel("gesture")
    # plt.xlabel("time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(),gestures[n],'-',label=n)
    # plt.legend(loc='upper right')

    ## Plot Lines for each event.
    for n in range(len(new_ideas)):
        x_val = new_ideas[n].to_pydatetime()
        ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
    plt.savefig(plot_title.replace(":","_") + '.pdf', dpi=150, format="pdf")
    plt.close()


def plot_score_posthoc_flux(gestures_frame,window,threshold):
    winlen = str(window) + "s"
    new_idea_difference_threshold = threshold #0.15

    # Setup Data.    
    transition_activity = transitions.calculate_transition_activity_for_window(gestures_frame,winlen)
    new_ideas = transitions.calculate_new_ideas(transition_activity, new_idea_difference_threshold)    
	
    #Plot and save the Gesture Score as a pdf:
    idx = gestures_frame.index
    ax = plt.figure(figsize=(25,10),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    title = "Post-Hoc: Gestures and Group Flux " + transition_activity.index[0].isoformat()
     # + " " + str(len(new_ideas)) + " new ideas with threshold " + str(new_idea_difference_threshold)
    plt.title(title + " (" + winlen + ", " + str(new_idea_difference_threshold) + ")")
    plt.ylabel("Gesture")
    plt.xlabel("Time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures_frame.columns:
        plt.plot_date(idx.to_pydatetime(),gestures_frame[n],'-',label=n)
    plt.legend(loc='upper right')
    
    transition_activity = transition_activity.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    idx = transition_activity.index
    plt.plot_date(idx.to_pydatetime(),transition_activity,'-',label=transition_activity.name)
    plt.ylabel("Flux")
    
    for n in range(len(new_ideas)):
        x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window / 2)
        ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax2.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        print x_val
    
    plt.savefig(title.replace(":","_") +'.pdf', dpi=150, format="pdf")
    plt.close()

# Testing ggplot (doesn't really work well)
def testing_ggplot():
    gestures['date'] = gestures.index
    #gestures_lng = pd.melt(gestures, id_vars=['date'], var_name="performer", value_name="gesture")
    gestures_lng = pd.melt(gestures, id_vars=['date'])
    gestures_lng.columns = ['date','performer','gesture']
    ggplot(aes(x='date', y='gesture', colour='performer'), data=gestures_lng) + geom_line() + ggtitle(plot_title) + scale_x_date(breaks=dates.SecondLocator(bysecond=[0]),labels="%H:%M:%S")

if __name__ == "__main__":
    #
    # Setup
    #
    parser = argparse.ArgumentParser(description='Plot Gestures and transitions of a set of Metatone CSVs. Input is the .log file')
    parser.add_argument('filename',help='A Metatone Classifier .log file to be converted.')
    args = parser.parse_args()
    input_filename = args.filename

    directory_path = input_filename.replace(".log","")[:-34]
    performance_name = input_filename.replace(".log","")[-34:]

    performance_time = time.strptime(performance_name[:19],'%Y-%m-%dT%H-%M-%S')
    plot_title = "Performance " + time.strftime('%y-%m-%d %H:%M',performance_time)

    print("Plot Title: " + plot_title)

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

    ## Do the plotting
    # plot_gesture_score_and_transitions(plot_title,events,gestures,metatone,online,touches,transitions_frame)
    plot_gesture_score(plot_title,events,gestures,metatone,online,touches,transitions_frame)
    # plot_score_posthoc_flux(gestures.fillna(0),5,0.25)
    print("Done! Plotted: " + plot_title)

