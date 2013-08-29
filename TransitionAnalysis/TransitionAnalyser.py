import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
import matplotlib.dates as dates
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

def one_step_transition(e1,e2):
    states_n = 5
    transition = np.zeros([states_n,states_n])
    transition[gesture_groups[e2]][gesture_groups[e1]] = transition[gesture_groups[e2]][gesture_groups[e1]] + 1
    return transition

def array_transitions(chain):
    output = []
    prev = -1
    for s in chain:
        curr = s
        if (prev != -1):
            output.append(one_step_transition(prev,curr))
        prev = s
    return np.sum(output,axis=0)

def create_transition_dataframe(states):
    output = pd.DataFrame(index = states.index, columns = states.columns)
    for col in states:
        prev = -1
        for s in states[col].index:
            curr = s
            if (prev != -1):
                output[col][s] = one_step_transition(states[col][prev],states[col][curr])
            prev = s
    return output

#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGesturePredictions.csv'
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGestureTargets.csv'
processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130803-18h-performance/MetatoneGestureScore20130803-18h38m10s.csv'

state_data = pd.read_csv(processed_file, index_col="time", parse_dates=True)

def plot_windowed_transitions():
    # Original (kind of wrong) windowing method...
    windowed_transitions = state_data.resample('15s',how=transition_matrix)
    windowed_transitions['group'] = windowed_transitions['jonathan'] + windowed_transitions['christina'] + windowed_transitions['yvonne'] + windowed_transitions['charles']
    # Plot and save each window...
    for n in range(len(windowed_transitions['group'])):
        title = windowed_transitions['group'].index[n].isoformat()
        print title
        plt.title(title)
        plt.imshow(windowed_transitions['group'].ix[n], cmap=plt.cm.binary, interpolation='nearest')
        plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
        plt.close()




alt_windowed = create_transition_dataframe(state_data).resample('15s',how=np.sum)
group_transitions = alt_windowed['jonathan'] + alt_windowed['christina'] + alt_windowed['yvonne'] + alt_windowed['charles']


def print_transition_plots(transitions):
    for n in range(len(transitions)):
        title = transitions.index[n].isoformat()
        print title
        plt.title(title)
        plt.imshow(transitions.ix[n], cmap=plt.cm.binary, interpolation='nearest')
        plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
        plt.close()

def diag_measure(mat):
    d = np.linalg.norm(mat.diagonal()) 
    m = np.linalg.norm(mat)
    if d == 0:
        d = 1
    return m/d


### Plot a "transition activity metric"

transition_activity = group_transitions.dropna().apply(diag_measure)
transition_activity.name = 'transition_activity'
transition_activity = transition_activity.resample('1s', fill_method='ffill')

#Plot and save the Gesture Score as a png:
idx = transition_activity.index
ax = plt.figure(figsize=(28,3),frameon=False,tight_layout=True).add_subplot(111)
ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
ax.xaxis.grid(True,which="minor")
ax.yaxis.grid()
title = "Transition Activity " + transition_activity.index[0].isoformat() 

plt.title(transition_activity.name)
plt.ylabel("changingness")
plt.xlabel("time")

plt.plot_date(idx.to_pydatetime(),transition_activity,'-',label=transition_activity.name)
plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
plt.close()

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#z = states_n * 10
#for row in transitions:
#    xs = np.arange(states_n)
#    ys = row
#    ax.bar(xs, ys, zs=z, zdir='y', color='r', alpha=0.8)
#    z = z - 10
#plt.show()
