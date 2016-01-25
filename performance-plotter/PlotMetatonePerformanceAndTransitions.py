#! /usr/bin/env python
# pylint: disable=line-too-long
"""
This script plots the data captured in Metatone Performances!
Uses all 6 CSV files output during the performance.
"""
from __future__ import print_function
import numpy as np
import pandas as pd
import transitions
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.cm as cm
from datetime import timedelta
#from ggplot import *
import time
import argparse

TRANSITION_STATES = {
    'stasis':0,
    'convergence':1,
    'divergence':2,
    'development':3}

#directory_path = '/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/'
#performance_name = '2014-03-17T18-30-57-MetatoneOSCLog'
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/'
# performance_name = '2014-03-17T18-09-46-MetatoneOSCLog'
# directory_path = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/'
# performance_name = '2014-03-17T17-40-14-MetatoneOSCLog'
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

def plot_gesture_score_and_transitions(plot_title, events, gestures, metatone, online, touches, transitions_frame):
    transitions_to_plot = transitions_frame.apply(lambda s: [TRANSITION_STATES[s[0]], s[1], s[2]], axis=1)
    new_ideas = events.index

    #Gesture Score:
    idx = gestures.index
    ax = plt.figure(figsize=(25, 10), frameon=False, tight_layout=True).add_subplot(311)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0, 10, 20, 30, 40, 50]))
    ax.xaxis.grid(True, which="minor")
    ax.yaxis.grid()
    plt.title(plot_title)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(), gestures[n], '-', label=n)
    plt.legend(loc='upper right')

    # Transition Type
    ax2 = plt.subplot(312, sharex=ax)
    ax2.xaxis.grid(True, which="major")
    ax2.yaxis.grid()
    idx = transitions_to_plot.index
    plt.plot_date(idx.to_pydatetime(),transitions_to_plot['transition_type'], '-', label='transition_type')
    plt.ylabel("transition type")
    plt.ylim(-0.25, 3.25)
    plt.yticks(np.arange(4),['sta', 'con', 'div', 'dev'])

    ## Transition Parameters
    ax3 = plt.subplot(313, sharex=ax)
    ax3.xaxis.grid(True, which="major")
    ax3.yaxis.grid()
    plt.plot_date(idx.to_pydatetime(), transitions_to_plot['spread'], '-', label='spread')
    plt.plot_date(idx.to_pydatetime(), transitions_to_plot['ratio'], '-', label='ratio')
    plt.ylim(-0.1,1.1)
    plt.legend(loc='upper right')
    plt.ylabel("transition params")

    ## Plot Lines for each event.
    for n in range(len(new_ideas)):
        x_val = new_ideas[n].to_pydatetime()
        ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax2.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax3.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
    plt.savefig(plot_title.replace(":", "_") + '.pdf', dpi=150, format="pdf")
    plt.close()

BW_PLOT = False
    
def plot_gesture_score(plot_title, events, gestures, metatone, online, touches, transitions_frame):
    """
    Plots the Gesture Score and New Idea events (dashed vertical lines).
    This is the version for the curating the digital chapter.
    Option to generate in black and white: (BW_PLOT)
    """
    print("Plotting Gestures and New-Ideas Only...")
    new_ideas = events.index
    if BW_PLOT:
        plt.style.use('grayscale')
    #figure_dimensions = (10,3.5) # good dimensions for curating the digital paper.
    figure_dimensions = (10,4.2) # good dimensions for thesis at 0.75\texheight
    #Gesture Score:
    idx = gestures.index
    ax = plt.figure(figsize=figure_dimensions, frameon=False, tight_layout=True, dpi=300).add_subplot(111)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.grid()
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(), gestures[n], '-', label=n)
    new_idea_colour = 'r'
    if BW_PLOT:
        new_idea_colour = 'black'
    ## Plot Lines for each event.
    for n in range(len(new_ideas)):
        x_val = new_ideas[n].to_pydatetime()
        ax.axvline(x=x_val, color=new_idea_colour, alpha=0.7, linestyle='--')
    out_title = plot_title.replace(":", "_").replace(" ", "-")
    plt.savefig(out_title + '.pdf', dpi=300, format="pdf")
    plt.close()
    print("Plot done.")

def plot_gesture_only_score(plot_title, gestures):
    """
    Plots a gesture score of gestures only - no new ideas!
    """
    idx = gestures.index
    # ax = plt.figure(figsize=(35,10),frameon=False,tight_layout=True).add_subplot(111)
    ax = plt.figure(figsize=(14, 4), frameon=False, tight_layout=True).add_subplot(111)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.grid()
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(), gestures[n], '-', label=n)
    # plt.legend(loc='upper right')
    plt.savefig(plot_title.replace(":", "_") + '.pdf', dpi=150, format="pdf")
    plt.close()

def plot_gestures_and_flux_score(plot_title, gestures, flux):
    """
    Plots a gesture score with flux values as well.
    """
    idx = gestures.index
    # ax = plt.figure(figsize=(35,10),frameon=False,tight_layout=True).add_subplot(111)
    ax = plt.figure(figsize=(14, 10), frameon=False, tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.grid()
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(), gestures[n], '-', label=n)
    # plt.legend(loc='upper right')

    ax2 = plt.subplot(212, sharex=ax)
    idx = flux.index
    plt.plot_date(idx.to_pydatetime(),flux,'-',label=flux.name)
    plt.ylabel("Flux")
    
    plt.savefig(plot_title.replace(":", "_") + '.pdf', dpi=150, format="pdf")
    plt.close()
    

def plot_score_posthoc_flux(gestures_frame):
    winlen = "15s"
    new_idea_difference_threshold = transitions.NEW_IDEA_THRESHOLD

    # Setup Data.    
    transition_matrices = transitions.calculate_group_transitions_for_window(gestures_frame, winlen)
    flux_series = transitions.calculate_flux_series(transition_matrices)
    new_ideas = transitions.calculate_new_ideas(flux_series, new_idea_difference_threshold)    
	
    #Plot and save the Gesture Score as a pdf:
    idx = gestures_frame.index
    ax = plt.figure(figsize=(14,6),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    title = "Post-Hoc: Gestures and Group Flux " + flux_series.index[0].isoformat()
     # + " " + str(len(new_ideas)) + " new ideas with threshold " + str(new_idea_difference_threshold)
    plt.title(title + " (" + winlen + ", " + str(new_idea_difference_threshold) + ")")
    plt.ylabel("Gesture")
    plt.xlabel("Time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures_frame.columns:
        plt.plot_date(idx.to_pydatetime(),gestures_frame[n],'-',label=n)
    plt.legend(loc='upper right')
    
    flux_series = flux_series.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    idx = flux_series.index
    plt.plot_date(idx.to_pydatetime(),flux_series,'-',label=flux_series.name)
    plt.ylabel("Flux")
    
    for n in range(len(new_ideas)):
        x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window / 2)
        ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        ax2.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
        print(x_val)
    
    plt.savefig(title.replace(":","_") +'.pdf', dpi=150, format="pdf")
    plt.close()

def main():
    """
    Main Script.
    """
    # Setup
    parser = argparse.ArgumentParser(description='Plot Gestures and transitions of a set of Metatone CSVs. Input is the .log file')
    parser.add_argument('filename',help='A Metatone Classifier .log file. The image will be created from CSV files which should be in the same directory.')
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
    #plot_score_posthoc_flux(gestures.fillna(0),15,0.3)
    print("Done! Plotted: " + plot_title)

if __name__ == "__main__":
    main()
