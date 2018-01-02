#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Supposed to load a gesture CSV and print the transition matrices. Somehow.
"""
from __future__ import print_function
import pandas as pd
import transitions
import matplotlib.pyplot as plt


DIRECTORY_PATH = "/Users/charles/Dropbox/Metatone/20150424-Study/20150429-Session1/logs/p1/"
PERFORMANCE_NAME = "2015-04-29T17-54-12-MetatoneOSCLog"


def print_transition_plots(transitions):
    """
    Saves a PDF of a heatmap plot of each transition matrix in the given list: transitions.
    """
    for transition_matrix in range(len(transitions)):
        state, spread, ratio = transitions.transition_state_measure(transitions.ix[transition_matrix])
        mat = transitions.transition_matrix_to_normal_transition_matrix(transitions.ix[transition_matrix])
        flux = transitions.flux_measure(mat)
        filename = transitions.index[transition_matrix].isoformat()
        title = transitions.index[transition_matrix].strftime('%Y-%m-%d %H:%M:%S')
        print(title)
        colours = plt.cm.Reds  # plt.cm.hot # plt.cm.autumn # plt.cm.binary for black and white
        # plt.title(title + " " + state + " " + str(spread) + " " + str(ratio))
        # plt.figure(figsize=(4.5,4),dpi=300)
        plt.figure(figsize=(5.5, 4), dpi=300)
        plt.title(title + " flux: " + str(round(flux, 3)))
        plt.imshow(mat, cmap=colours, interpolation='nearest', vmin=0.0, vmax=1.0)
        plt.colorbar()  # shows the legend
        labels = ["none", "taps", "swipes", "swirls", "combo"]
        plt.xticks([0, 1, 2, 3, 4], labels)
        plt.yticks([0, 1, 2, 3, 4], labels)
        plt.savefig(filename.replace(":", "_") + '.pdf', dpi=300, format="pdf")
        plt.close()
        # TODO make sure stochastic calculation doesn't fail on nonzero matrices.


def main():
    """ Do the stuff. """
    print("Going to make a lot of PDFs now...")
    gestures_path = DIRECTORY_PATH + PERFORMANCE_NAME + '-gestures.csv'
    gestures = pd.read_csv(gestures_path, index_col='time', parse_dates=True)
    transition_matrices = transitions.calculate_group_transitions_for_window(gestures, '15s')
    transitions.print_transition_plots(transition_matrices)

if __name__ == "__main__":
    main()
