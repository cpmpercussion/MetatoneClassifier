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



##
## Settings up to July 2014 - as used in the 17/3 concert
## and CHI2014 demos etc.
##
NEW_IDEA_THRESHOLD = 0.3
TRANSITIONS_WINDOW = '15s'

## Old values for the NEW_IDEA_THRESHOLD.
#new_idea_difference_threshold = 0.15
# new_idea_difference_threshold = 0.80 # 1-norm version (experimental)
#new_idea_difference_threshold = 0.5 # 1-norm version (experimental)
# new_idea_difference_threshold = 0.3 # new 14/3/2014
#new_idea_difference_threshold =  0.3# new 6/7/2014

##
## Experimental Settings post July 2014...
##

## Int values for Gesture codes.
NUMBER_GESTURES = 9
gesture_codes = {
	'N': 0,
	'FT': 1,
	'ST': 2,
	'FS': 3,
	'FSA': 4,
	'VSS': 5,
	'BS': 6,
	'SS': 7,
	'C': 8}

NUMBER_GROUPS = 5
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

# Is this function unused?
def transition_matrix(chains):
	states_n = NUMBER_GROUPS
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

# Is this function unused?
def array_transitions(chain):
	output = []
	prev = -1
	for s in chain:
		curr = s
		if (prev != -1):
			output.append(one_step_transition(prev,curr))
		prev = s
	return np.sum(output,axis=0)



def one_step_transition(e1,e2):
	"""
        Calculates a transition matrix between two states.
        """
	matrix = np.zeros([NUMBER_GROUPS,NUMBER_GROUPS])
	matrix[gesture_groups[e2]][gesture_groups[e1]] = matrix[gesture_groups[e2]][gesture_groups[e1]] + 1
	return matrix

def multi_step_transition(chain):
        """
        Calculates the transition matrix of a whole list of states.
        """
        matrix = np.zeros([NUMBER_GROUPS,NUMBER_GROUPS])
        if len(chain) < 2:
                return matrix
        for i in xrange(1, len(chain)):
                e2 = chain[i]
                e1 = chain[i-1]
                matrix[gesture_groups[e2]][gesture_groups[e1]] = matrix[gesture_groups[e2]][gesture_groups[e1]] + 1
        return matrix

def create_transition_dataframe_old_method(states):
        """
        No longer used.
        """
	output = pd.DataFrame(index = states.index, columns = states.columns)
	for col in states:
		prev = -1
		for s in states[col].index:
			curr = s
			if (prev != -1):
                                from_state = states[col][prev]
                                to_state = states[col][curr]
                                matrix = one_step_transition(from_state,to_state)
				output[col][s] = matrix
			prev = s
	return output

def create_transition_dataframe(states):
        """
        Given a the gesture states of a single player, calculates a dataframe of one-step transition matrices.
        Used in the calculate_group_transitions_for_window function which is used in the classifyPerformance loop.
        """
        output = np.zeros_like(states)
	#output = pd.DataFrame(index = states.index, columns = states.columns)
	#index = states.index
        #columns = states.columns
        dictionary_output = {}
        for col in states:
                matrices = [np.nan]
		prev = -1
		for s in states[col].index:
			curr = s
			if (prev != -1):
                                from_state = states[col][prev]
                                to_state = states[col][curr]
                                matrix = one_step_transition(from_state,to_state)
				matrices.append(matrix)
			prev = s
                dictionary_output[col] = matrices
	df = pd.DataFrame(index = states.index, data = dictionary_output)
        return df

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
	
def flux_measure(mat):
	"""
	Measure of a transition matrix's flux. Given a numpy matrix M with diagonal D, 
	returns the ||M||_1 - ||D||_1 / ||M||_1
	Maximised at 1 when nothing on diagonal, 
	Minimised at 0 when everything on diagonal.
	Name is deprecated and will be migrated to "flux" in later code.
	"""
	mat = np.array(mat)
	d = np.linalg.norm(mat.diagonal(),1) # |d|_1 
	m = sum(sum(abs(mat))) # |M|_1
	measure = (m - d) / m # Flux.
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

# @profile
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
	"""
	Applies the two-norm to each value in vecs, a dictionary of vectors, 
	Returns true if there are any vectors with identical norms.
	"""
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
	"""
        Sums an array of transition matrices.
        Used for resampling during performances as well as creating a whole-performance transition matrix.
        """
	out = np.sum(tran_arr,axis=0).tolist()
	return out

def print_transition_plots(transitions):
	"""Saves a PDF of a heatmap plot of each transition matrix in the given list: transitions."""
	for n in range(len(transitions)):
		state,spread,ratio = transition_state_measure(transitions.ix[n])
		title = transitions.index[n].isoformat()
		print title
		plt.title(title + " " + state + " " + str(spread) + " " + str(ratio))
		plt.imshow(transitions.ix[n], cmap=plt.cm.binary, interpolation='nearest')
		plt.savefig(title.replace(":","_") + '.pdf', dpi=150, format="pdf")
		plt.close()

##
# User Functions:
##
def calculate_transition_activity(states_frame):
	"""
	Shortcut for calculate_transition_activity_for_window with default window size.
	"""
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	return calculate_transition_activity_for_window(states_frame,TRANSITIONS_WINDOW)


def calculate_transition_activity_for_window(states_frame,window_size):
	"""
	Returns a time-series of flux using the window_size (string) to divide 
	the given states_frame.
	(this function should be retired)
	"""
	if(not isinstance(states_frame,pd.DataFrame) or states_frame.empty):
		return None
	group_transitions = calculate_group_transitions_for_window(states_frame,window_size)
	if (isinstance(group_transitions,type(None))):
		return None
	return calculate_flux_series(group_transitions)

def calculate_flux_series(transition_matrices):
	"""
	Returns a time-series of flux from a series of transition matrices
	"""
	if (isinstance(transition_matrices,type(None))):
		return None
	flux_series = transition_matrices.dropna().apply(flux_measure)
	flux_series.name = 'flux_activity'
	return flux_series


def calculate_new_ideas(flux_series, threshold):
	"""
	Given a time series of flux throughout the performance, returns
	a time series of points where the flux has increased above the given
	threshold.
	"""
	return flux_series.ix[flux_series.diff() > threshold]

def is_new_idea_with_threshold(flux_series, threshold):
	"""
	Returns True if the flux of the most recent pair of transitions 
	has increased above the given threshold. This suggests that a
	"new idea" has occured in the ensemble.
	"""
	if not isinstance(flux_series, pd.TimeSeries):
		return False
	measure = flux_series[-2:].diff().dropna()
	if ((not measure.empty) and measure[0] > threshold):
		return True
	else:
		return False

def is_new_idea(flux_series):
	"""Shortcut for is_new_idea_with_threshold with built in threshold."""
	if not isinstance(flux_series, pd.TimeSeries):
		return False
	if (is_new_idea_with_threshold(flux_series,NEW_IDEA_THRESHOLD)):
		return True
	else:
		return False


def current_transition_state(states_frame):
	"""
	Returns the Current Transition State (string), spread (float), and ratio(float)
	Calculates a new series of transition matrices each time!
	(should be retired)
	"""
	transitions = calculate_group_transitions_for_window(states_frame,'15s')
	if(not isinstance(transitions,pd.TimeSeries)):
		return None
	state, spread, ratio = transition_state_measure(transitions[-1])
	return state, spread, ratio


# @profile
def calculate_group_transitions_for_window(states_frame,window_size):
	"""
	Calculates the (group) transition matrices for a given window size 
	over the states_frame DataFrame.
	"""
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
	"""TODO: Use this function to return different kinds of events."""
	return ("nothing","device_id",0)
