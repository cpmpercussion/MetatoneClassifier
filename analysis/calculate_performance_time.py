#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Calculates performance length in seconds for each member of a Metatone ensemble.
Performance length for each performer is defined as the time delta between the first touch in the performance and
that performer''s final touch.
The final touch may have to be adjusted due to accidental touches at the end of the log.
"""
from __future__ import print_function
import pandas as pd
import time

DIRECTORY_PATH = "/Users/charles/Dropbox/Metatone/20150424-Study/20150429-Session1/logs/p1/"
PERFORMANCE_NAME = "2015-04-29T17-54-12-MetatoneOSCLog"


def calculate_performance_lengths(touches):
    """
    Calculates the Individual Performance Lengths for each performer and
    returns a dictionary.
    """
    performers = touches['device_id'].unique()
    first_touch = touches[:1].index[0].to_datetime()
    last_touch = touches[-1:].index[0].to_datetime()
    performer_first_touches = {}
    performer_last_touches = {}
    performance_lengths = {}
    print("Total performance length was: " + str((last_touch - first_touch).total_seconds()))
    for performer_id in performers:
        performer_touches = touches.ix[touches['device_id'] == performer_id]
        performer_first_touches[performer_id] = performer_touches[:1].index[0].to_datetime()
        performer_last_touches[performer_id] = performer_touches[-1:].index[0].to_datetime()
        performer_length = (performer_touches[-1:].index[0].to_datetime() - first_touch).total_seconds()
        performance_lengths[performer_id] = performer_length
        print("Performer: " + performer_id)
        print("Length was: " + str(performer_length))
    print(str(performance_lengths))
    return {touches[:1].index[0]: performance_lengths}


def main():
    """
    Calculate performance length for each performer.
    """
    performance_time = time.strptime(PERFORMANCE_NAME[:19], '%Y-%m-%dT%H-%M-%S')
    plot_title = "Performance " + time.strftime('%y-%m-%d %H:%M', performance_time)
    print(plot_title)

    # events_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-events.csv'
    # gestures_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-gestures.csv'
    # metatone_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-metatone.csv'
    # online_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-online.csv'
    touches_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-touches.csv'
    # transitions_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-transitions.csv'

    # events = pd.read_csv(events_path, index_col='time', parse_dates=True)
    # gestures = pd.read_csv(gestures_path, index_col='time', parse_dates=True)
    # metatone = pd.read_csv(metatone_path, index_col='time', parse_dates=True)
    # online = pd.read_csv(online_path, index_col='time', parse_dates=True)
    touches = pd.read_csv(touches_path, index_col='time', parse_dates=True)
    # transitions_frame = pd.read_csv(transitions_path, index_col='time', parse_dates=True)
    calculate_performance_lengths(touches)

if __name__ == "__main__":
    main()
