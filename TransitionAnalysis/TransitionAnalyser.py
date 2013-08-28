import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

## Int values for Gesture codes.
gesture_codes = {
    'N': 0,
    'FT': 1,
    'ST': 2,
    'FS': 3,
    'FSA': 4,
    'VSS': 5,
    'BS': 6,
    'SS': 7,
    'C': 8,
    '?': 9}
    
gesture_groups = {
    0 : 0,
    1 : 1,
    2 : 1,
    3 : 2,
    4 : 2,
    5 : 3,
    6 : 3,
    7 : 3,
    8 : 4,
    9 : 4}

def transition_matrix(chains):
    states_n = 5
    #transitions = np.zeros([states_n,states_n])
    output = []
    for col in chains:
        transitions = np.zeros([states_n,states_n])
        curr_chain = chains[col].tolist()
        curr_chain = map(int,curr_chain)
        prev = -1
        for s in curr_chain:
            curr = s
            if (prev != -1):
                transitions[gesture_groups[curr]][gesture_groups[prev]] = transitions[gesture_groups[curr]][gesture_groups[prev]] + 1
            prev = s
        output.append(transitions)
    return output
    #return np.reshape(transitions,-1)


    
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGesturePredictions.csv'
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGestureTargets.csv'
processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130803-18h-performance/MetatoneGestureScore20130803-18h38m10s.csv'

state_data = pd.read_csv(processed_file, index_col="time", parse_dates=True)


windowed_transitions = state_data.resample('30s',how=transition_matrix)
windowed_transitions['group'] = windowed_transitions['jonathan'] + windowed_transitions['christina'] + windowed_transitions['yvonne'] + windowed_transitions['christina']


#for row in transitions:
#    total = sum(row)
#    row = map((lambda x: x / total),row)

#transitions = map((lambda row: map((lambda x: x if (sum(row) == 0) else x / sum(row)),row)),transitions)

#plt.imshow(transitions, cmap=plt.cm.binary, interpolation='nearest')
#plt.show()



plt.imshow(windowed_transitions['group'].ix[0], cmap=plt.cm.binary, interpolation='nearest')
plt.show()

### Need to plot each row to a different place!




fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
z = states_n * 10
for row in transitions:
    xs = np.arange(states_n)
    ys = row
    ax.bar(xs, ys, zs=z, zdir='y', color='r', alpha=0.8)
    z = z - 10
plt.show()

