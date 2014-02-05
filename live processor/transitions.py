## Transition Functions Module
## 


import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from datetime import timedelta

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
    
def diag_measure(mat):
    # 1.3 is a good split for "New events"
    mat = np.array(mat)
    d = np.linalg.norm(mat.diagonal()) 
    m = np.linalg.norm(mat)
    if d == 0:
        d = 1
    return m/d

def diag_measure2(mat):
    # 1.3 is a good split for "New events"
    mat = np.array(mat)
    d = np.linalg.norm(mat.diagonal()) 
    m = np.linalg.norm(mat)
    if d == 0:
        d = 0.5
        print m/d
    return m/d
    
def diag_measure_1_norm(mat):
    # 1.3 is a good split for "New events"
    mat = np.array(mat)
    d = np.linalg.norm(mat.diagonal(),1) 
    m = np.linalg.norm(mat,1)
    return m - d
    

def transition_sum(tran_arr):
    out = np.sum(tran_arr,axis=0).tolist()
    return out

def print_transition_plots(transitions):
    for n in range(len(transitions)):
        title = transitions.index[n].isoformat()
        print title
        plt.title(title)
        plt.imshow(transitions.ix[n], cmap=plt.cm.binary, interpolation='nearest')
        plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
        plt.close()

def calculate_transition_activity(states_frame):
    if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
        return []
    ## TODO check for empty frame
    ## check for frame that's too small??
    window_size = '15s'
    new_idea_difference_threshold = 0.15
    transitions = create_transition_dataframe(states_frame).dropna()
    if(transitions.empty):
        return []
    cols = [transitions[n] for n in transitions.columns]
    for c in range(len(cols)):
        if (c == 0):
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]       
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(window_size,how=transition_sum)
    transition_activity = group_transitions.dropna().apply(diag_measure)
    transition_activity.name = 'transition_activity'
    new_ideas = transition_activity.ix[transition_activity.diff() > new_idea_difference_threshold]
    return transition_activity

def is_new_idea(transitions):
    if not isinstance(transitions, pd.TimeSeries):
        raise TypeError, "Transitions is not a TimeSeries"
    measure = transitions[-2:].diff().dropna()
    new_idea_difference_threshold = 0.15
    if (measure and measure[0] > new_idea_difference_threshold):
        return True
    else:
        return False
