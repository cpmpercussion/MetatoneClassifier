#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Should calculate a lot of stats about all the performances in the data folder. Also prints each gesture-score.
"""
from __future__ import print_function
import os
import pandas as pd
import PlotMetatonePerformanceAndTransitions
import time
import datetime
import transitions

EVENTS_PATH = '-events.csv'
GESTURES_PATH = '-gestures.csv'
METATONE_PATH = '-metatone.csv'
ONLINE_PATH = '-online.csv'
TOUCHES_PATH = '-touches.csv'
TRANSITIONS_PATH = '-transitions.csv'

DEVICE_SEATS = {
    "BD49B35A-8999-4987-9759-8D3F28D1292B":1,
    "9A5116EA-2793-4C75-AC93-524C9EF550FD":2,
    "1A56F5DD-C5B6-4E56-8690-E5A12BAA7E78":3,
    "24C41EC3-7ECC-40DA-B942-7ABE23017E74":4}

class MetatonePerformanceLog:
    """
    Class to contain dataframes of a single metatone performance logs.
    Must be initialised with a log_path.
    """
    def __init__(self, log_path):
        print("Loading logs for " + log_path)
        performance_path = log_path.replace(".log", "")
        self.performance_title = performance_path[-34:]
        self.touches = pd.read_csv(performance_path + TOUCHES_PATH, index_col='time', parse_dates=True)
        self.events = pd.read_csv(performance_path + EVENTS_PATH, index_col='time', parse_dates=True)
        self.raw_new_ideas = self.events[self.events["event_type"] == "new_idea"]["event_type"].count()
        self.screen_change_new_ideas = self.count_new_idea_interface_changes()
        self.gestures = pd.read_csv(performance_path + GESTURES_PATH, index_col='time', parse_dates=True)
        self.transitions = pd.read_csv(performance_path + TRANSITIONS_PATH, index_col='time', parse_dates=True)
        self.metatone = pd.read_csv(performance_path + METATONE_PATH, index_col='time', parse_dates=True)
        self.online = pd.read_csv(performance_path + ONLINE_PATH, index_col='time', parse_dates=True)
        # These next two lines still use reduced gestures...
        self.ensemble_transition_matrix = transitions.calculate_group_transition_matrix(self.gestures.dropna())
        self.ensemble_transition_matrix = transitions.transition_matrix_to_stochastic_matrix(self.ensemble_transition_matrix)

    def count_new_idea_interface_changes(self):
        """ 
        Counts new_idea events that resulted in an interface change, 
        that is, with time in between greater than 10 seconds 
        """
        NEW_IDEA_DELAY = 10
        screen_changed_column = {}
        last_time = datetime.datetime(1, 1, 1, 0, 0, 0, 0)
        for index, row in self.events[self.events["event_type"] == "new_idea"].iterrows():
            if (index.to_datetime() - last_time).total_seconds() > NEW_IDEA_DELAY:
                screen_changed_column[index] = True
                last_time = index
            else: 
                screen_changed_column[index] = False
        screen_changed = pd.TimeSeries(screen_changed_column)
        self.events["screen_changed"] = screen_changed
        return screen_changed[screen_changed == True].count()

    def count_button_interface_changes(self):
        return self.metatone[self.metatone["label"] == "CompositionStep"]["label"].count()

    def button_interface_changes_by_performer(self):
        """
        Returns a dict of the number of UI interactions for each device_id in the performance.
        """
        performer_changes = {}
        for perf in self.performers():
            performer_changes[perf] = self.metatone[self.metatone["device_id"] == perf]["label"].count()
        return {self.touches[:1].index[0]:performer_changes}
 
    def ensemble_flux(self):
        return transitions.flux_measure(self.ensemble_transition_matrix)

    def ensemble_entropy(self):
        return transitions.entropy_measure(self.ensemble_transition_matrix)

    def performers(self):
        """
        Returns the list of performers in this performance
        """
        return self.touches['device_id'].unique()

    def performance_length(self):
        """
        Returns the total length of the performance (first touch to last touch)
        """
        first_touch = self.touches[:1].index[0].to_datetime()
        last_touch = self.touches[-1:].index[0].to_datetime()
        return (last_touch - first_touch).total_seconds()

    def performer_lengths(self):
        """
        Returns the individual performers' performance lengths
        """
        performers = self.performers()
        first_touch = self.touches[:1].index[0].to_datetime()
        performer_first_touches = {}
        performer_last_touches = {}
        performance_lengths = {}
        for performer_id in performers:
            performer_touches = self.touches.ix[self.touches['device_id'] == performer_id]
            performer_first_touches[performer_id] = performer_touches[:1].index[0].to_datetime()
            performer_last_touches[performer_id] = performer_touches[-1:].index[0].to_datetime()
            performer_length = (performer_touches[-1:].index[0].to_datetime() - first_touch).total_seconds()
            performance_lengths[performer_id] = performer_length
            # print("Performer: " + performer_id + " Length was: " + str(performer_length))
        return {self.touches[:1].index[0]:performance_lengths}

    def print_gesture_score(self):
        """
        Prints a gesture-score using the script procedure
        """
        performance_time = time.strptime(self.performance_title[:19], '%Y-%m-%dT%H-%M-%S')
        plot_title = "gesture-score-" + time.strftime('%y-%m-%d-%H-%M', performance_time)
        PlotMetatonePerformanceAndTransitions.plot_gesture_score(plot_title, self.events, self.gestures, self.metatone, self.online, self.touches, self.transitions)

def main():
    """Load up all the performances and do some stats"""
    log_files = []
    performances = []
    for local_file in os.listdir("data"):
        if local_file.endswith(".log"):
            log_files.append("data/" + local_file)
    print("Loading the performances.")
    for log in log_files:
        performances.append(MetatonePerformanceLog(log))
    print("Finding the lengths.")
    performer_length_dict = {}
    for perf in performances:
        performer_length_dict.update(perf.performer_lengths())
    performance_length_frame = pd.DataFrame.from_dict(performer_length_dict, orient="index")
    performance_length_frame['time'] = performance_length_frame.index
    performers = performances[0].performers().tolist()
    long_performance_lengths = pd.melt(performance_length_frame, id_vars=['time'], value_vars=performers)
    long_performance_lengths = long_performance_lengths.replace({'variable':DEVICE_SEATS})
    long_performance_lengths.to_csv("performance_lengths.csv")
    print("Creating Gesture Scores.")
    for perf in performances:
        perf.print_gesture_score() ## Prints out a gesture-score pdf for reference.

if __name__ == '__main__':
    main()
