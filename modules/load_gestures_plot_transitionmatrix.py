#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Supposed to load a gesture CSV and print the transition matrices. Somehow.
"""
from __future__ import print_function
import pandas as pd
import transitions

DIRECTORY_PATH = "/Users/charles/Dropbox/Metatone/20150424-Study/20150429-Session1/logs/p1/"
PERFORMANCE_NAME = "2015-04-29T17-54-12-MetatoneOSCLog"

def main():
    """ Do the stuff. """
    print("Going to make a lot of PDFs now...")
    gestures_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-gestures.csv'
    gestures = pd.read_csv(gestures_path, index_col='time', parse_dates=True)
    transition_matrices = transitions.calculate_group_transitions_for_window(gestures, '15s')
    transitions.print_transition_plots(transition_matrices)

if __name__ == "__main__":
    main()
