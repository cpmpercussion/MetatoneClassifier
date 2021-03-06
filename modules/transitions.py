"""
Transition Functions Module
Charles Martin 2013-2014

Calculates and manipulates transition matrices.
"""
from __future__ import print_function
import pandas as pd
import numpy as np
from scipy.stats import entropy
from datetime import timedelta
from datetime import datetime

##
# Settings up to July 2014 - as used in the 17/3 concert
# and CHI2014 demos etc.
##
NEW_IDEA_THRESHOLD = 0.3
TRANSITIONS_WINDOW = '15s'
# Old values for the NEW_IDEA_THRESHOLD.
# new_idea_difference_threshold = 0.15
# new_idea_difference_threshold = 0.80 # 1-norm version (experimental)
# new_idea_difference_threshold = 0.5 # 1-norm version (experimental)
# new_idea_difference_threshold = 0.3 # new 14/3/2014
# new_idea_difference_threshold =  0.3# new 6/7/2014

# Int values for Gesture codes.
NUMBER_GESTURES = 9
GESTURE_CODES = {
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
GESTURE_GROUPS = {
    0: 0,
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 3,
    8: 4,
    9: 4}

# NUMBER_GROUPS = 10
# GESTURE_GROUPS = {
# 	0 : 0,
# 	1 : 1,
# 	2 : 2,
# 	3 : 3,
# 	4 : 4,
# 	5 : 5,
# 	6 : 6,
# 	7 : 7,
# 	8 : 8,
# 	9 : 9}

#####################
#
# Full Transition Matrix Calculations.
#
#####################


def full_one_step_transition(e1, e2):
    """
    Calculates a full transition matrix between two states.
    """
    matrix = full_empty_transition_matrix()
    matrix[e2][e1] += 1
    return matrix


def full_empty_transition_matrix():
    """
    Returns a full empty transition matrix.
    """
    return np.zeros([NUMBER_GESTURES, NUMBER_GESTURES])  # Full gesture matrix


def full_create_transition_dataframe(states):
    """
    Given a the gesture states of a single player,
    calculates a dataframe of full one-step transition matrices.
    """
    dictionary_output = {}
    for col in states:
        matrices = [full_empty_transition_matrix()]
        prev = -1
        for index_loc in states[col].index:
            curr = index_loc
            if prev != -1:
                from_state = states.at[prev, col]
                to_state = states.at[curr, col]
                matrix = full_one_step_transition(from_state, to_state)
                matrices.append(matrix)
            prev = index_loc
            dictionary_output[col] = matrices
    return pd.DataFrame(index=states.index, data=dictionary_output)


def calculate_full_group_transition_matrix(states_frame):
    """
    Returns the group's transition matrix for a whole performance.
    """
    if not isinstance(states_frame, pd.DataFrame) or states_frame.empty:
        return None
    transitions = full_create_transition_dataframe(states_frame.dropna()).dropna()
    if transitions.empty:
        return None
    cols = [transitions[n] for n in transitions.columns]
    for c in range(len(cols)):
        if c == 0:
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]
    group_transitions = group_transitions.dropna()
    group_matrix = transition_sum(group_transitions)
    return group_matrix

#####################
#
# Creating Reduced Transition Matrices
#
#####################


def one_step_transition(e1, e2):
    """
    Calculates a transition matrix between two states.
    """
    matrix = np.zeros([NUMBER_GROUPS, NUMBER_GROUPS])
    try:
        matrix[GESTURE_GROUPS[e2]][GESTURE_GROUPS[e1]] += 1
    except:
        matrix = np.zeros([NUMBER_GROUPS, NUMBER_GROUPS])
    return matrix


def empty_transition_matrix():
    """
    Returns an empty transition matrix.
    """
    return np.zeros([NUMBER_GROUPS, NUMBER_GROUPS])  # Reduced Gesture Groups.


def multi_step_transition(chain):
    """
    Calculates the transition matrix of a whole sequence of states.
    """
    matrix = np.zeros([NUMBER_GROUPS, NUMBER_GROUPS])
    if len(chain) < 2:
        return matrix
    for i in range(1, len(chain)):  # FIXME: is this accounting for all members of the chain?
        e2 = chain[i]
        e1 = chain[i - 1]
        matrix[GESTURE_GROUPS[e2]][GESTURE_GROUPS[e1]] += 1  # Reduced Gesture Groups.
        return matrix


def create_transition_dataframe(states):
    """
    Given a dataframe of gesture states for each player, calculates a
    new dataframe of one-step transition matrices.
    """
    output = states.copy()
    for col in states:
        output[col] = map(one_step_transition, states[col].shift(), states[col])
    return output


def compare_tm_dataframes(tm_1, tm_2):
    """
    Compares two dataframes of transition matrices.
    Returns true if index and each column are equal, otherwise false.
    Prints each stage - this could be removed.
    """
    if False not in (tm_1.index == tm_2.index).tolist():
        print("Indexes the same")
    else:
        print("Indexes different :-(")
        return False
    try:
        for col in tm_1:
            if False not in map(np.array_equal, tm_1[col].tolist(), tm_2[col].tolist()):
                print("col ok!")
            else:
                print("col fail!")
                return False
    except:
        print("cols not equal!")
        return False
    print("seemed to pass!")
    return True


def transition_sum(tran_arr):
    """
    Sums an array of transition matrices. Used for resampling during
    performances as well as creating a whole-performance transition
    matrix.
    """
    out = np.sum(tran_arr, axis=0).tolist()
    return out


def transition_matrix_to_stochastic_matrix(trans_matrix):
    """
    Convert a transition matrix with entries >1 to a stochastic matrix
    where rows sum to 1. Rows with zero in all entries stay as zero!
    """
    try:
        result = map((lambda x: map((lambda n: 0 if n == 0 else n / sum(x)), x)), trans_matrix)
    except ZeroDivisionError:
        print("Fail! Zero division error when making stochastic matrix.")
        result = trans_matrix
    return result


def transition_matrix_to_normal_transition_matrix(trans_matrix):
    """
    Convert a transition matrix with entries > 1 to a normal
    transition matrix ( under the element-wise 1-norm i.e. ||M||_1 =
    1). Zero-matrices stay zero.
    """
    m = sum(sum(abs(np.array(trans_matrix))))
    if m > 0:
        result = trans_matrix / m
    else:
        result = trans_matrix
    return result


def reduce_matrix_to_groups(mat):
    """
    Converts a 9x9 matrix of all gesture transitions to the simpler
    gesture groups.
    """
    group_matrix = np.zeros([NUMBER_GROUPS, NUMBER_GROUPS])
    for i in range(NUMBER_GESTURES):
        for j in range(NUMBER_GESTURES):
            group_matrix[GESTURE_GROUPS[i]][GESTURE_GROUPS[j]] += mat[i][j]
    return group_matrix

#####################
#
# Matrix Measures
#
#####################


def flux_measure(mat):
    """
    Measure of a transition matrix's flux. Given a numpy matrix M with
    diagonal D, returns the ||M||_1 - ||D||_1 / ||M||_1 Maximised at 1
    when nothing on diagonal, Minimised at 0 when everything on
    diagonal.
    """
    mat = np.array(mat)
    d = np.linalg.norm(mat.diagonal(), 1)  # |d|_1
    m = sum(sum(abs(mat)))  # |M|_1
    if m == 0:
        # Take care of case of empty matrix
        # returning 0 is wrong but more benign than NaN
        measure = 0
    else:
        measure = (m - d) / m  # Flux.
    return measure


def entropy_measure(mat):
    """Measures a transition matrix's entropy in the information
    theoretic sense. H(P) = -\sum_{i,j}p_{ij}\log_2(p_{ij}) Uses
    scipy.stats.entropy
    """
    return entropy(np.reshape(mat, len(mat)**2), base=2)


#####################
#
# Ensemble State Calculations --- probably time to retire these.
#
#####################


def vector_ratio(mat, vec):
    """Ratio of Vector to Matrix using the 1-Norm."""
    vec_size = np.linalg.norm(vec, 1)
    mat_size = sum(sum(abs(mat)))
    if mat_size == 0:
        return 1  # take care of zero denominator - zero isn't too bad.
    else:
        return vec_size / mat_size


def vector_spread(vec):
    """
    Spread of data along a vector - 0 if all data in one entry, 1 if evenly spread.
    """
    vec_norm = np.linalg.norm(vec, 1)
    if vec_norm == 0:
        spread = 1  # take care of zero denominator
    else:
        spread = np.linalg.norm(vec) / vec_norm
    rootn = np.sqrt(len(vec))
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
    cols = [mat[:, x] for x in range(mat.shape[1])]
    vecs = {}
    vecs["stasis"] = diag
    vecs["convergence"] = max(cols, key=np.linalg.norm)
    vecs["divergence"] = max(rows, key=np.linalg.norm)
    # TODO - fix this so that if there is no max, we get "development"
    if dict_vecs_equal_under_norm(vecs):
        state = dict_vecs_special_case_state(vecs)
    else:
        state = max(vecs, key=(lambda x: np.linalg.norm(vecs.get(x))))

    if state == 'development':
        spread = 1  # not a great choice todo better idea.
        ratio = 1 - vector_ratio(mat, diag)
    else:
        spread = vector_spread(vecs[state])
        ratio = vector_ratio(mat, vecs[state])
    return state, spread, ratio


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
    """
    Test function - unused.
    """
    state = None
    normvecs = {k: np.linalg.norm(v) for k, v in vecs.iteritems()}
    singles = [k for k, v in normvecs.iteritems() if normvecs.values().count(v) == 1]
    if not singles:
        state = 'stasis'
    elif len(singles) == 1 and 'stasis' in singles:
        state = 'development'
    elif len(singles) == 1 and 'convergence' in singles:
        state = 'divergence'
    elif len(singles) == 1 and 'divergence' in singles:
        state = 'convergence'
    return state


#####################
#
# User functions - used in classifier and other processing scripts
#
#####################


def calculate_flux_series(transition_matrices):
    """
    Returns a time-series of flux from a series of transition matrices
    """
    if isinstance(transition_matrices, type(None)):
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
    # if (not measure.empty):
    #     print("Flux Increase: " + str(measure[0])) # printing flux increase should be removed later.
    if (not measure.empty) and measure[0] > threshold:
        return True
    else:
        return False


def is_new_idea(flux_series):
    """
    Shortcut for is_new_idea_with_threshold with built in threshold.
    """
    if not isinstance(flux_series, pd.TimeSeries):
        return False
    if is_new_idea_with_threshold(flux_series, NEW_IDEA_THRESHOLD):
        return True
    else:
        return False


def calculate_group_transitions_for_window(states_frame, window_size):
    """
    Calculates the (group) transition matrices for a given window size
    over the states_frame DataFrame.
    """
    if not isinstance(states_frame, pd.DataFrame) or states_frame.empty:
        return None
    transitions = create_transition_dataframe(states_frame).dropna()
    if transitions.empty:
        return None
    cols = [transitions[n] for n in transitions.columns]
    for column in range(len(cols)):
        if column == 0:
            group_transitions = cols[column]
        else:
            group_transitions = group_transitions + cols[column]
    group_transitions = group_transitions.dropna()
    group_transitions = group_transitions.resample(window_size, how=transition_sum)
    return group_transitions


def transition_sum_then_flux(transitions):
    # do a transition sum, then output the flux.
    sum_transition = transition_sum(transitions)
    flux_value = flux_measure(sum_transition)
    return flux_value


def calculate_rolling_flux_for_window(states_frame):
    """
    Finally Working
    """
    if not isinstance(states_frame, pd.DataFrame) or states_frame.empty:
        return None
    transition_series = create_transition_dataframe(states_frame).dropna()

    cols = [transition_series[n] for n in transition_series.columns]
    for column in range(len(cols)):
        if column == 0:
            group_transitions = cols[column]
        else:
            group_transitions = group_transitions + cols[column]
    group_transitions = group_transitions.dropna()
    window = 15
    flux_series = pd.concat([(pd.Series(transition_sum_then_flux(group_transitions.iloc[i:i + window]), index=[group_transitions.index[i + window]])) for i in range(len(group_transitions) - window)])
    return flux_series


def calculate_group_transition_matrix(states_frame):
    """
    Returns the group's transition matrix for a whole performance.
    """
    if not isinstance(states_frame, pd.DataFrame) or states_frame.empty:
        return None
    transitions = create_transition_dataframe(states_frame).dropna()
    if transitions.empty:
        return None
    cols = [transitions[n] for n in transitions.columns]
    for c in range(len(cols)):
        if c == 0:
            group_transitions = cols[c]
        else:
            group_transitions = group_transitions + cols[c]
    group_transitions = group_transitions.dropna()
    group_matrix = transition_sum(group_transitions)
    return group_matrix


def trim_gesture_frame(gestures):
    """
    Returns the last 60 seconds of entries in a dataframe with a timeseries index.
    """
    current_time = datetime.now()
    delta = timedelta(seconds=-60)
    cutoff = current_time + delta
    return gestures.ix[gestures.index > cutoff]


##
# Generative Agent Stuff
##


def weighted_choice(weights):
    """
    Returns a random index from a list weighted by the list's entries.
    """
    rnd = np.random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


# #####################
# #
# # Plotting Transition events
# # Commenting this for now.
# #
# #####################


# def print_transition_plots(transitions):
#     """
#     Saves a PDF of a heatmap plot of each transition matrix in the given list: transitions.
#     """
#     for transition_matrix in range(len(transitions)):
#         state, spread, ratio = transition_state_measure(transitions.ix[transition_matrix])
#         mat = transition_matrix_to_normal_transition_matrix(transitions.ix[transition_matrix])
#         flux = flux_measure(mat)
#         filename = transitions.index[transition_matrix].isoformat()
#         title = transitions.index[transition_matrix].strftime('%Y-%m-%d %H:%M:%S')
#         print(title)
#         colours = plt.cm.Reds # plt.cm.hot # plt.cm.autumn # plt.cm.binary for black and white
#         # plt.title(title + " " + state + " " + str(spread) + " " + str(ratio))
#         # plt.figure(figsize=(4.5,4),dpi=300)
#         plt.figure(figsize=(5.5, 4), dpi=300)
#         plt.title(title + " flux: " + str(round(flux, 3)))
#         plt.imshow(mat, cmap=colours, interpolation='nearest', vmin=0.0,vmax=1.0)
#         plt.colorbar()  # shows the legend
#         labels = ["none", "taps", "swipes", "swirls", "combo"]
#         plt.xticks([0, 1, 2, 3, 4], labels)
#         plt.yticks([0, 1, 2, 3, 4], labels)
#         plt.savefig(filename.replace(":", "_") + '.pdf', dpi=300, format="pdf")
#         plt.close()
#         # TODO make sure stochastic calculation doesn't fail on nonzero matrices.
