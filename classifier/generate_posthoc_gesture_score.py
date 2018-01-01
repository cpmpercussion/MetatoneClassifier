#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Classifies Gestures from Metatone Touch Log at 1s intervals. Gestures are output as a CSV file and PDF plot.
datetime, name, x_pos, y_pos, vel
"""
from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import timedelta
import argparse
import metatone_classifier
import transitions

CLASSIFIER = metatone_classifier.MetatoneClassifier()


def feature_vector_from_row_time(row, frame, name):
    """
    Returns ONE feature vector from the given dataframe before "time"
    """
    time = row.name
    delta = timedelta(seconds=-5)
    frame = frame.between_time((time + delta).time(), time.time())
    if frame.empty:
        return [-1, -1, name, 0, 0, 0, 0, 0, 0]
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_mvmt = frame.ix[frame['velocity'] != 0]
    frame_centroid = frame[['x_pos', 'y_pos']].mean()
    frame_std = frame[['x_pos', 'y_pos']].std().fillna(0)

    feature_vector = {
        'freq': frame['device_id'].count(),
        'device_id': name,
        'touchdown_freq': frame_touchdowns['device_id'].count(),
        'movement_freq': frame_mvmt['device_id'].count(),
        'centroid_x': frame_centroid[0],
        'centroid_y': frame_centroid[1],
        'std_x': frame_std[0],
        'std_y': frame_std[1],
        'velocity': frame['velocity'].mean()
    }
    return feature_vector


def feature_vector_from_frame(frame):
    """
    Return one feature vector from a complete dataframe.
    """
    if frame.empty:
        return [-1, -1, "name", 0, 0, 0, 0, 0, 0]
    frame_touchdowns = frame.ix[frame.velocity == 0]
    frame_mvmt = frame.ix[frame.velocity != 0]
    frame_centroid = frame[['x_pos', 'y_pos']].mean()
    frame_std = frame[['x_pos', 'y_pos']].std().fillna(0)
    feature_vector = {
        'freq': frame.device_id.count(),
        'device_id': frame.device_id.ix[0],
        'touchdown_freq': frame_touchdowns.device_id.count(),
        'movement_freq': frame_mvmt.device_id.count(),
        'centroid_x': frame_centroid[0],
        'centroid_y': frame_centroid[1],
        'std_x': frame_std[0],
        'std_y': frame_std[1],
        'velocity': frame.velocity.mean()
    }
    return feature_vector


def gesture_prediction_from_frame(frame):
    """
    Return one gesture prediction from a dataframe
    """
    feature_vector = feature_vector_from_frame(frame)
    return CLASSIFIER.classifier.predict(feature_vector[metatone_classifier.FEATURE_VECTOR_COLUMNS])


def generate_rolling_feature_frame(messages, name):
    """
    Takes a message frame and creates a gesture frame with calculations every 1s.
    Returns the generated gesture frame.
    """
    features = metatone_classifier.feature_frame(messages)
    features = features.resample('1s')
    # is it possible to make this next step faster?
    features = features.apply(feature_vector_from_row_time, axis=1, frame=messages, name=name)
    return features


def generate_gesture_frame(touchlog_frame):
    """
    Creates a dataframe of classified gestures at 1s intervals.
    """
    names = touchlog_frame['device_id'].unique()
    gesture_pred = pd.DataFrame(touchlog_frame['device_id'].resample('1s', how='count'))
    # ticks = gesture_pred.resample('10s').index.to_pydatetime()
    for name in names:
        print("Processing Performer data for: " + name)
        performer_features = generate_rolling_feature_frame(touchlog_frame.ix[touchlog_frame['device_id'] == name], name)
        performer_features['pred'] = CLASSIFIER.classifier.predict(performer_features[metatone_classifier.FEATURE_VECTOR_COLUMNS])
        gesture_pred[name] = performer_features['pred']
    gesture_pred = gesture_pred.fillna(0)
    gesture_pred = gesture_pred[names]
    gesture_pred[names] = gesture_pred[names].astype(int)
    return gesture_pred


def generate_flux_frame(gesture_frame):
    """
    Generates tms at 1s intervals and calculates a rolling flux calculation.
    """
    window_size = "15s"
    fluxes = pd.DataFrame(index=gesture_frame.index)
    fluxes = gesture_frame.apply(flux_calculation_from_row, axis=1,frame=gesture_frame,window=window_size)
    return fluxes


def flux_calculation_from_row(row,frame,window):
    window = "15s"
    time = row.name
    delta = timedelta(seconds=-37)
    frame = frame.between_time((time + delta).time(), time.time())
    transition_matrices = transitions.calculate_group_transitions_for_window(frame, window)
    flux_series = transitions.calculate_flux_series(transition_matrices)
    newidea = transitions.is_new_idea(flux_series)
    flux_series = flux_series.dropna()
    flux_latest = 0
    if flux_series.count() > 0:
        flux_latest = flux_series.tolist()[-1]
    return flux_latest


def flux_calculation_from_row_roll(frame):
    window = "15s"
    print(frame)
    transition_matrices = transitions.calculate_group_transitions_for_window(frame, window)
    flux_series = transitions.calculate_flux_series(transition_matrices)
    newidea = transitions.is_new_idea(flux_series)
    flux_series = flux_series.dropna()
    flux_latest = 0
    if flux_series.count() > 0:
        flux_latest = flux_series.tolist()[-1]
    return flux_latest


def generate_flux_diff_frame(gesture_frame):
    """
    Calculates a rolling calculation of flux differences at the same interval as the gestures.
    """
    # Should be able to do this by selecting two date ranges, and then
    # using the direct group-transition / flux function. TODO -
    # implement this idea, and make it work properly so that flux diff
    # can be plotted and modelled for thesis.

    window_size = "15s"
    flux_diffs = pd.DataFrame(index=gesture_frame.index)
    flux_diffs = gesture_frame.apply(flux_diff_calculation_from_row, axis=1, frame=gesture_frame, window=window_size)
    return flux_diffs


def flux_diff_calculation_from_row(row,frame,window):
    time = row.name
    delta = timedelta(seconds=-37)
    frame = frame.between_time((time + delta).time(), time.time())
    transition_matrices = transitions.calculate_group_transitions_for_window(frame, window)
    flux_series = transitions.calculate_flux_series(transition_matrices)
    newidea = transitions.is_new_idea(flux_series)
    flux_series = flux_series.dropna()
    flux_diff = 0
    if flux_series.count() > 1:
        flux_diff = flux_series[-2:].diff().dropna().tolist()[0]
    return flux_diff


def generate_gesture_plot(names, gesture_frame):
    """
    Probably a bad function for creating gesture plots
    """
    outname = gesture_frame.index[0].strftime('%Y-%m-%dT%H-%M-%S-MetatonePostHoc-gestures')
    performance_date = gesture_frame.index[0].strftime('%Y-%m-%d %H:%M:%S')
    idx = gesture_frame.index
    axes = plt.figure(figsize=(28, 8), frameon=False, tight_layout=True).add_subplot(111)
    axes.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0, 30]))
    axes.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    axes.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0, 10, 20, 30, 40, 50]))
    axes.xaxis.grid(True, which="minor")
    axes.yaxis.grid()
    plt.title("Post-hoc Gesture Score for Performance: " + performance_date)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for name in names:
        plt.plot_date(idx.to_pydatetime(), gesture_frame[name], '-', label=name)
    plt.legend(loc='upper right')
    plt.savefig(outname + '.pdf', dpi=300, format="pdf")
    plt.close()


def plot_gestures_and_flux_score(plot_title, gestures, flux, flux_diffs):
    """
    Plots a gesture score with flux values as well - this one suffers the window bug
    """
    idx = gestures.index
    # ax = plt.figure(figsize=(35,10),frameon=False,tight_layout=True).add_subplot(111)
    ax = plt.figure(figsize=(14, 6), frameon=False, tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.grid()
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    plt.ylabel("gesture")
    for n in gestures.columns:
        plt.plot_date(idx.to_pydatetime(), gestures[n], '-', label=n)
    # Plot Flux Data
    ax2 = plt.subplot(212, sharex=ax)
    idx = flux.index
    plt.plot_date(idx.to_pydatetime(),flux,'-',label=flux.name)
    plt.ylabel("flux")
    # Possible New Ideas Stage
    # new_ideas = flux_diffs.ix[flux_diffs > transitions.NEW_IDEA_THRESHOLD]
    # new_ideas = new_ideas.index
    # new_idea_colour = 'r'
    # for n in range(len(new_ideas)):
    #     x_val = new_ideas[n].to_pydatetime()
    #     ax.axvline(x=x_val, color=new_idea_colour, alpha=0.7, linestyle='--')
    #     ax2.axvline(x=x_val, color=new_idea_colour, alpha=0.7, linestyle='--')
    # Output Stage
    plt.savefig(plot_title.replace(":", "_") + '.pdf', dpi=300, format="pdf")
    plt.close()


def plot_score_posthoc_flux(title, gestures_frame):
    """
    Plots gestures and generates post-hoc rolling flux on a 15s
    (actually 15 sample) window.
    """
    # Setup Data.
    flux_series = transitions.calculate_rolling_flux_for_window(gestures_frame)
    # Setup Plot
    idx = gestures_frame.index
    # What's a good size for the figure? (14,10) seems like a nice proportion
    ax = plt.figure(figsize=(10.5,7.5),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,15,30,45]))
    # ax.xaxis.grid(True, which="minor")
    ax.yaxis.grid()
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for n in gestures_frame.columns:
        plt.plot_date(idx.to_pydatetime(), gestures_frame[n], '-', label=n)   
    flux_series = flux_series.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    # ax2.xaxis.grid(True, which="minor")
    idx = flux_series.index
    plt.plot_date(idx.to_pydatetime(), flux_series, '-', label=flux_series.name)
    plt.ylabel("flux")
    # # Plot New Ideas
    # for n in range(len(new_ideas)):
    #     x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window / 2)
    #     ax.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
    #     ax2.axvline(x=x_val, color='r', alpha=0.7, linestyle='--')
    #     print(x_val)
    # Output Stage
    plt.savefig(title.replace(":", "_") + '.pdf', dpi=300, format="pdf")
    plt.close()


def plot_score_and_new_ideas(gestures_frame):
    winlen = "15s"
    window = 15
    new_idea_difference_threshold = 0.15
    #transitions.NEW_IDEA_THRESHOLD
    # Setup Data.    
    transition_matrices = transitions.calculate_group_transitions_for_window(gestures_frame, winlen)
    flux_series = transitions.calculate_flux_series(transition_matrices)
    new_ideas = transitions.calculate_new_ideas(flux_series, new_idea_difference_threshold)    
    #Plot and save the Gesture Score as a pdf:
    idx = gestures_frame.index
    ax = plt.figure(figsize=(10,5),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0])) # right!
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,15,30,45]))
    #ax.xaxis.grid(True, which="minor")
    ax.yaxis.grid()
    title = "Post-Hoc: Gestures and Group Flux " + flux_series.index[0].isoformat()
    plt.ylabel("gesture")
    #plt.xlabel("Time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in gestures_frame.columns:
        plt.plot_date(idx.to_pydatetime(),gestures_frame[n],'-',label=n)
    #plt.legend(loc='upper right')
    flux_series = flux_series.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    idx = flux_series.index
    plt.plot_date(idx.to_pydatetime(),flux_series,'-',label=flux_series.name)
    plt.ylabel("flux")
    for n in range(len(new_ideas)):
        x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window / 2)
        #x_val = new_ideas.index[0].to_pydatetime() + timedelta(seconds = window / 2) # just look at the first new-idea
        ax.axvline(x=x_val, color='r', alpha=1, linestyle='--')
        ax2.axvline(x=x_val, color='r', alpha=1, linestyle='--')
        print(x_val)
    plt.savefig(title.replace(":","_") +'.pdf', dpi=300, format="pdf")
    plt.close()


def post_hoc_transition_analysis_for_thesis(gesture_filename):
    gestures = pd.read_csv(gesture_filename, index_col='time', parse_dates=True)
    gestures_first_time = str(gestures.index[0])
    plot_score_posthoc_flux(gestures_first_time + "-gesture-and-flux", gestures)
    transition_series = transitions.calculate_group_transitions_for_window(gestures, "15s")
    flux_series = transitions.calculate_flux_series(transition_series)
    new_ideas = transitions.calculate_new_ideas(flux_series, 0.15)
    print(new_ideas)
    plot_score_and_new_ideas(gestures)
    transitions.print_transition_plots(transition_series)

    # GESTURES_FILE = "/Users/charles/src/metatone-analysis/data/2015-04-29T18-34-58-MetatoneOSCLog-touches-posthoc-gestures.csv"

# gestures = pd.read_csv(GESTURES_FILE, index_col='time', parse_dates=True)
# plot_score_posthoc_flux("2014-08-14T18-40-57-gestures-and-flux",gestures)
# flux_values = generate_flux_frame(gestures)
# flux_values.name = "Flux"
# flux_diffs = generate_flux_diff_frame(gestures)
# flux_diffs.name = "Flux_Difference"
# plot_gestures_and_flux_score("2014-08-14T18-40-57-gestures-and-flux",gestures,flux_values,flux_diffs)
# flux_series = transitions.calculate_rolling_flux_for_window(gestures)
# flux_series = transitions.calculate_rolling_flux_for_window(gestures)


def generate_phd_plots():
    # An Interesting Study Quartet Improv
    GESTURES_FILE = "/Users/charles/src/metatone-analysis/data/2015-04-29T18-34-58-MetatoneOSCLog-touches-posthoc-gestures.csv"
    post_hoc_transition_analysis_for_thesis(GESTURES_FILE)

    GESTURES_FILE = "/Users/charles/src/metatone-analysis/data/2014-07-19T13-58-10-MetatoneOSCLog-touches-posthoc-gestures.csv"
    post_hoc_transition_analysis_for_thesis(GESTURES_FILE)

    # An Interesting Study Trio Improv
    GESTURES_FILE = "/Users/charles/Desktop/flux-calculation-test/2014-07-19T15-18-35-MetatoneOSCLog-touches-posthoc-gestures.csv"
    post_hoc_transition_analysis_for_thesis(GESTURES_FILE)

    # Colour Music Opening
    GESTURES_FILE = "/Users/charles/src/metatone-analysis/data/2014-08-14T18-40-57-MetatoneOSCLog-touches-posthoc-gestures.csv"
    post_hoc_transition_analysis_for_thesis(GESTURES_FILE)

    # Gesture Study You Are Here Premiere
    GESTURES_FILE = "/Users/charles/src/metatone-analysis/data/2014-03-17T18-09-46-MetatoneOSCLog-touches-posthoc-gestures.csv"
    post_hoc_transition_analysis_for_thesis(GESTURES_FILE)


def main():
    """
    Takes a touch csv file as input, creates a gesture score csv and an image plot.
    """
    parser = argparse.ArgumentParser(description='Classifies Gestures from Metatone Touch Log at 1s intervals. Gestures are output as a CSV file and PDF plot.')
    parser.add_argument('filename', help='A Metatone Touch CSV file to be classified.')
    args = parser.parse_args()
    touchlog_file = args.filename
    print("Classifying Touch CSV file...")

    messages = pd.read_csv(touchlog_file, index_col="time", parse_dates=True)
    gesture_pred = generate_gesture_frame(messages)

    names = messages['device_id'].unique()
    generate_gesture_plot(names, gesture_pred)

    outname = gesture_pred.index[0].strftime('%Y-%m-%dT%H-%M-%S-MetatonePostHoc-gestures')
    gesture_pred.to_csv(outname + '.csv', date_format='%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':
    main()
