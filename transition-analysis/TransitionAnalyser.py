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
    

def print_transition_plots(transitions):
    for n in range(len(transitions)):
        title = transitions.index[n].isoformat()
        print title
        plt.title(title)
        plt.imshow(transitions.ix[n], cmap=plt.cm.binary, interpolation='nearest')
        plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
        plt.close()

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

##
##
##
## Load the data
##
##

#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGesturePredictions.csv'
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/markov-experiments/20130427-MetatoneGestureTargets.csv'

## Metatone iPad Only Performances.
##
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130420/MetatoneAutoGestureScore20130420-14h58m50s.csv'
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130421/MetatoneAutoGestureScore20130421-11h47m10s.csv'
#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130427/MetatoneAutoGestureScore20130427-17h46m15s.csv'
processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130803-17h-rehearsal/MetatoneGestureScore20130803-17h11m00s.csv'

#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130504-14h23/MetatoneAutoGestureScore20130504-14h24m20s.csv'


#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130803-18h-performance/MetatoneGestureScore20130803-18h38m10s.csv'

#processed_file = '/Users/charles/Dropbox/Metatone/touch-point-performance-analysis/metatone-performances/20130803-18h-performance/MetatoneGestureScore20130803-18h52m55s.csv'


state_data = pd.read_csv(processed_file, index_col="time", parse_dates=True)

##
## Plot the windowed Transition Matrices
##
def plot_transitions_different_windows():
    for winlen in ['15s','20s','25s','30s','35s','40s']:
        #winlen = '15s'
        alt_windowed = create_transition_dataframe(state_data)
        group_transitions = alt_windowed['jonathan'] + alt_windowed['christina'] + alt_windowed['yvonne'] + alt_windowed['charles']
        group_transitions = group_transitions.dropna()
        group_transitions = group_transitions.resample(winlen,how=transition_sum)
        
        plt.figure(figsize=(16,12),frameon=False,tight_layout=True)
        #plt.suptitle("Group Transitions for Performance: " + group_transitions.index[0].strftime('%Y-%m-%d %H:%M:%S'))
        for n in range(len(group_transitions)):
            title = group_transitions.index[n].strftime('%H:%M:%S')
            print title
            plt.subplot(8,6,n+1)
            plt.title(title)
            plt.imshow(np.array(group_transitions[n]), cmap=plt.cm.gray_r, interpolation='nearest')
        #plt.tight_layout()
        #plt.show()
        title = "Group Transitions for Performance: " + group_transitions.index[0].strftime('%Y-%m-%d %H:%M:%S')
        plt.savefig(title.replace(":","_") + " " + winlen + '.png', dpi=150, format="png")
        plt.close()


##
## Plot the "Changeyness Metric"
##
def plot_changeyness_different_windows():
    for winlen in ['5s','10s','15s','20s','25s','30s','35s','40s']:
        #winlen = '15s'
        print "Trying window length of:" + winlen
        alt_windowed = create_transition_dataframe(state_data)
        group_transitions = alt_windowed['jonathan'] + alt_windowed['christina'] + alt_windowed['yvonne'] + alt_windowed['charles']
        group_transitions = group_transitions.dropna()
        group_transitions = group_transitions.resample(winlen,how=transition_sum)
        
        transition_activity = group_transitions.dropna().apply(diag_measure)
        transition_activity.name = 'transition_activity'
        transition_activity = transition_activity.resample('1s', fill_method='ffill')
        
        #Plot and save as png
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
        plt.savefig(title.replace(":","_") + " " + winlen + '.png', dpi=150, format="png")
        plt.close()


def plot_old_windowed_transitions():
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

def plot_score_and_changeyness():
    window_seconds = 15
    winlen = str(window_seconds) + "s"
    new_idea_difference_threshold = 0.15
    
    print "Calculating changeyness for window:" + winlen
    alt_windowed = create_transition_dataframe(state_data)
    #group_transitions = alt_windowed['jonathan'] + alt_windowed['christina'] + alt_windowed['yvonne'] + alt_windowed['charles']
    #for
    cols = [alt_windowed[n] for n in alt_windowed.columns]
    for c in range(len(cols)):
        if (c == 0):
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]     
    
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(winlen,how=transition_sum)
    transition_activity = group_transitions.dropna().apply(diag_measure)
    transition_activity.name = 'transition_activity'
    
    new_ideas = transition_activity.ix[transition_activity.diff() > new_idea_difference_threshold]
    
    
    #Plot and save the Gesture Score as a png:
    idx = state_data.index
    ax = plt.figure(figsize=(25,10),frameon=False,tight_layout=True).add_subplot(211)
    ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
    ax.xaxis.grid(True,which="minor")
    ax.yaxis.grid()
    title = "Transition Activity and Changeyness" + transition_activity.index[0].isoformat() + " "+ str(len(new_ideas)) + " new ideas"
    plt.title(title)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5,8.5)
    plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])
    for n in state_data.columns:
        plt.plot_date(idx.to_pydatetime(),state_data[n],'-',label=n)
    plt.legend(loc='upper right')
    
    #for n in range(len(new_ideas)):
    #    x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window_seconds)
    #    ax.axvline(x=x_val, color='r')
    #    print x_val
    
    transition_activity = transition_activity.resample('1s', fill_method='ffill')
    ax2 = plt.subplot(212, sharex=ax)
    idx = transition_activity.index
    plt.plot_date(idx.to_pydatetime(),transition_activity,'-',label=transition_activity.name)
    plt.ylabel("changeyness")
    
    for n in range(len(new_ideas)):
        x_val = new_ideas.index[n].to_pydatetime() + timedelta(seconds = window_seconds / 2)
        ax.axvline(x=x_val, color='r')
        ax2.axvline(x=x_val, color='r')
        print x_val
    
    #plt.xlabel("time")
    plt.savefig(title.replace(":","_") + " " + winlen + '.png', dpi=150, format="png")
    plt.close()
    


##
## Try scatter plot of diag_measured data
##
def scatter_plots_of_changeyness():
    winlen = '5s'
    print "Trying window length of:" + winlen
    alt_windowed = create_transition_dataframe(state_data)

    cols = [alt_windowed[n] for n in alt_windowed.columns]
    for c in range(len(cols)):
        if (c == 0):
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]
    
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(winlen,how=transition_sum)
    transition_activity = group_transitions.dropna().apply(diag_measure)
    transition_activity.name = 'transition_activity'
    plt.scatter(transition_activity,[1]*len(transition_activity))
    
    winlen = '10s'
    print "Trying window length of:" + winlen
    alt_windowed = create_transition_dataframe(state_data)

    cols = [alt_windowed[n] for n in alt_windowed.columns]
    for c in range(len(cols)):
        if (c == 0):
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]     
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(winlen,how=transition_sum)
    transition_activity = group_transitions.dropna().apply(diag_measure)
    transition_activity.name = 'transition_activity'
    plt.scatter(transition_activity,[2]*len(transition_activity))
    
    winlen = '15s'
    print "Trying window length of:" + winlen
    alt_windowed = create_transition_dataframe(state_data)

    cols = [alt_windowed[n] for n in alt_windowed.columns]
    for c in range(len(cols)):
        if (c == 0):
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(winlen,how=transition_sum)
    transition_activity = group_transitions.dropna().apply(diag_measure)
    transition_activity.name = 'transition_activity'
    plt.scatter(transition_activity,[3]*len(transition_activity))
    plt.show()


plot_score_and_changeyness()
