##
## Experiment in defining and classifying state data from Metatone Performances using a set of interaction states.
##
import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


## Definition of Interaction States
interaction_states = {
    'independent-static' : 0,
    'independent-dynamic' : 1,
    'connected-static' : 2,
    'connected-dynamic' : 3,
    'semi-connected-static' : 4,
    'semi-connected-dynamic' : 5}
    
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = it.tee(iterable)
    next(b, None)
    return it.izip(a, b)



processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGesturePredictions.csv'
chains = pd.read_csv(processed_file, index_col="time", parse_dates=True)

for x,y in pairwise(chains.iterrows()):
    # figure out how x and y change.

