"""
Transition Functions Module
Charles Martin 2013-2014

Calculates and manipulates transition matrices.
"""

import pandas as pd
import numpy as np
import itertools as it
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from datetime import timedelta
from datetime import datetime
import random

NUMBER_STATES = 5

##
## Settings up to July 2014 - as used in the 17/3 concert
## and CHI2014 demos etc.
##
NEW_IDEA_THRESHOLD = 0.3
TRANSITIONS_WINDOW = '15s'

##
## Experimental Settings post July 2014...
##
##

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
	states_n = NUMBER_STATES
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

def one_step_transition(e1,e2):
	"""Calculates the transition between two states."""
	states_n = NUMBER_STATES
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
	"""Given a numpy matrix mat, returns the 2-norm of the matrix divided by 
	the two norm of the diagonal provided the diagonal is not the zero vector.
	(In this case returns the 2-norm of the matrix.)"""
	mat = np.array(mat)
	d = np.linalg.norm(mat.diagonal()) 
	m = np.linalg.norm(mat)
	if d == 0:
		d = 1
	return m/d

def diag_measure2(mat):
	"""
	Given a numpy matrix mat, returns the 2-norm of the matrix divided by 
	the two norm of the diagonal provided the diagonal is not the zero vector.
	(In this case returns the 2-norm of the matrix divided by 2.)
	"""
	# 1.3 is a good split for "New events"
	mat = np.array(mat)
	d = np.linalg.norm(mat.diagonal()) 
	m = np.linalg.norm(mat)
	if d == 0:
		d = 0.5
		print m/d
	return m/d
	
def diag_measure_1_norm(mat):
	"""
	Measure of a transition matrix's flux. Given a numpy matrix M with diagonal D, 
	returns the ||M||_1 - ||D||_1 / ||M||_1
	Maximised at 1 when nothing on diagonal, 
	Minimised at 0 when everything on diagonal.
	"""
	mat = np.array(mat)
	d = np.linalg.norm(mat.diagonal(),1) # |d|_1 
	m = sum(sum(abs(mat))) # |M|_1
	measure = (m - d) / m 
	return measure


def vector_ratio(mat,vec):
	"""Ratio of Vector to Matrix using the 1-Norm."""
	return np.linalg.norm(vec,1) / sum(sum(abs(mat)))

def vector_spread(vec):
	"""Spread of data along a vector - 0 if all data in one entry, 1 if evenly spread."""
	spread = np.linalg.norm(vec) / np.linalg.norm(vec,1)
	rootn =  np.sqrt(len(vec))
	spread = rootn * (1.0 - spread) / (1 - rootn)
	spread = np.fabs(spread)
	return spread

def transition_state_measure(mat):
	"""
	Chooses the vector with the most data in the matrix and 
	returns a state interpretation as well as the spread of data along
	that vector.
	"""
	mat = np.array(mat)
	diag = mat.diagonal()
	rows = [x for x in mat]
	cols = [mat[:,x] for x in range(mat.shape[1])]
	vecs = {}
	vecs["stasis"] = diag
	vecs["convergence"] = max(cols, key=np.linalg.norm)
	vecs["divergence"] = max(rows, key=np.linalg.norm)
	#TODO - fix this so that if there is no max, we get "development"
	if (dict_vecs_equal_under_norm(vecs)):
		state = dict_vecs_special_case_state(vecs)
	else:
		state = max(vecs, key = (lambda x: np.linalg.norm(vecs.get(x))))
	
	if (state == 'development'):
		spread = 1 # not a great choice todo better idea.
		ratio = 1 - vector_ratio(mat,diag)
	else:    
		spread = vector_spread(vecs[state])
		ratio = vector_ratio(mat,vecs[state])
	return state,spread,ratio

def dict_vecs_equal_under_norm(vecs):
	normvecs = [np.linalg.norm(v) for k,v in vecs.iteritems()]
	mults = [x for x in normvecs if normvecs.count(x) > 1]
	if mults:
		return True
	else:
		return False

def dict_vecs_special_case_state(vecs):
	state = None
	normvecs = {k: np.linalg.norm(v) for k,v in vecs.iteritems()}
	singles = [k for k,v in normvecs.iteritems() if normvecs.values().count(v) == 1]
	if (not singles):
		state = 'stasis'
	elif (len(singles) == 1 and 'stasis' in singles):
		state ='development'
	elif (len(singles) == 1 and 'convergence' in singles):
		state ='divergence'
	elif (len(singles) == 1 and 'divergence' in singles):
		state ='convergence'
	return state

def transition_sum(tran_arr):
	"""Sums an array of transition matrices."""
	out = np.sum(tran_arr,axis=0).tolist()
	return out

def print_transition_plots(transitions):
	for n in range(len(transitions)):
		state,spread,ratio = transition_state_measure(transitions.ix[n])
		title = transitions.index[n].isoformat()
		print title
		plt.title(title + " " + state + " " + str(spread) + " " + str(ratio))
		plt.imshow(transitions.ix[n], cmap=plt.cm.binary, interpolation='nearest')
		plt.savefig(title.replace(":","_") + '.png', dpi=150, format="png")
		plt.close()

##
# User Functions:
##

def calculate_transition_activity(states_frame):
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	return calculate_transition_activity_for_window(states_frame,TRANSITIONS_WINDOW)

def calculate_transition_activity_for_window(states_frame,window_size):
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	new_idea_difference_threshold = 0.80 # 1-norm version (experimental)
	group_transitions = calculate_group_transitions_for_window(states_frame,window_size)
	if (isinstance(group_transitions,type(None))):
		return None
	transition_activity = group_transitions.dropna().apply(diag_measure_1_norm) # changed to 1-norm version.
	transition_activity.name = 'transition_activity'
	return transition_activity

def calculate_new_ideas(transition_activity, threshold):
	return transition_activity.ix[transition_activity.diff() > threshold]

def is_new_idea_with_threshold(transitions, threshold):
	"""
	Returns True if current transitions suggest a "new_idea" event according to the current threshold.
	"""
	if not isinstance(transitions, pd.TimeSeries):
		return None
	measure = transitions[-2:].diff().dropna()
	# if (measure and measure[0] > threshold):
	if ((not measure.empty) and measure[0] > threshold):
		return True
	else:
		return False

#
# Shortcut for is_new_idea_with_threshold with built in threshold
#
def is_new_idea(transitions):
	if not isinstance(transitions, pd.TimeSeries):
		return None
	#new_idea_difference_threshold = 0.15
	#new_idea_difference_threshold = 0.5 # 1-norm version (experimental)
	# new_idea_difference_threshold = 0.3 # new 14/3/2014
	new_idea_difference_threshold = NEW_IDEA_THRESHOLD # new 6/7/2014
	if (is_new_idea_with_threshold(transitions,new_idea_difference_threshold)):
		return True
	else:
		return False

def current_transition_state(states_frame):
	"""Returns the Current Transition State (string), spread (float), and ratio(float)"""
	# Returns the current transition state as a string
	transitions = calculate_group_transitions_for_window(states_frame,'15s')
	if(not isinstance(transitions,pd.TimeSeries)):
		return None
	state, spread, ratio = transition_state_measure(transitions[-1])
	return state, spread, ratio

def calculate_group_transitions_for_window(states_frame,window_size):
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	transitions = create_transition_dataframe(states_frame).dropna()
	if(transitions.empty):
		return None
	cols = [transitions[n] for n in transitions.columns]
	for c in range(len(cols)):
		if (c == 0):
			group_transitions = cols[c]
		else:
			group_transitions = group_transitions + cols[c]       
	group_transitions = group_transitions.dropna()
	group_transitions = group_transitions.resample(window_size,how=transition_sum)
	return group_transitions

def calculate_group_transition_matrix(states_frame):
	"""Returns the group's transition matrix for a whole performance."""
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	transitions = create_transition_dataframe(states_frame).dropna()
	if(transitions.empty):
		return None
	cols = [transitions[n] for n in transitions.columns]
	for c in range(len(cols)):
		if (c == 0):
			group_transitions = cols[c]
		else:
			group_transitions = group_transitions + cols[c]       
	group_transitions = group_transitions.dropna()
	group_matrix = transition_sum(group_transitions)
	return group_matrix

def trim_gesture_frame(gestures):
	""" Returns the last 60 seconds of entries in a dataframe with a timeseries index."""
	current_time = datetime.now()
	delta = timedelta(seconds=-60)
	cutoff = current_time + delta
	return gestures.ix[gestures.index > cutoff]

##
## GenerativeAgent Stuff
##

def transition_matrix_to_stochastic_matrix(trans_matrix):
	""" Convert a transition matrix with entries >1 to a stochastic matrix where rows sum to 1. """
	result = map((lambda x: map((lambda n: n/sum(x)),x)), trans_matrix)
	return result

def weighted_choice(weights):
	""" Returns a random index from a list weighted by the list's entries."""
	rnd = random.random() * sum(weights)
	for i, w in enumerate(weights):
		rnd -= w
		if rnd < 0:
			return i

#
# TODO - fixup functionality for this method - should return different kinds of events (or something for no event).
#
def is_event(states_frame):
	return ("nothing","device_id",0)
