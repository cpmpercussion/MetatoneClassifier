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
    
processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGesturePredictions.csv'
chains = pd.read_csv(processed_file, index_col="time", parse_dates=True)

    
states_n = len(gesture_codes)
transitions = np.zeros([states_n,states_n])
curr_chain = chains['charles'].tolist()
curr_chain = map(int,curr_chain)

prev = -1
for s in curr_chain:
    curr = s
    print ("Current: " + str(curr) + " Previous: " + str(prev))
    
    if (prev != -1):
        # increment matrix entry
        print("Mapping "+str(curr) + " P: " + str(prev))
        transitions[curr][prev] = transitions[curr][prev] + 1
        
    prev = s

for row in transitions:
    total = sum(row)
    row = map((lambda x: x / total),row)

transitions = map((lambda row: map((lambda x: x if (sum(row) == 0) else x / sum(row)),row)),transitions)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

z = states_n * 10

for row in transitions:
    xs = np.arange(states_n)
    ys = row

    # You can provide either a single color or an array. To demonstrate this,
    # the first bar of each set will be colored cyan.
    ax.bar(xs, ys, zs=z, zdir='y', color='r', alpha=0.8)
    z = z - 10

plt.show()