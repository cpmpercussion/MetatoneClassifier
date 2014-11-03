import pandas as pd
import numpy as np
import fullGestureTransitions
import random

# parser = argparse.ArgumentParser(description='Do something with a CSV file.')
# parser.add_argument('filename',help='A Metatone Gesture CSV file to be used.')
# args = parser.parse_args()
# gesture_file = args.filename

gesture_file = 'data/MetatoneAutoGestureScore20130803-18h38m11s.csv'
gestures = pd.read_csv(gesture_file, index_col='time', parse_dates=True)
transition_matrices = fullGestureTransitions.create_transition_dataframe(gestures)

group_matrix = fullGestureTransitions.calculate_group_transition_matrix(gestures)
group_matrix = fullGestureTransitions.transition_matrix_to_stochastic_matrix(group_matrix)

def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

m = np.array(group_matrix)
s = 0

s = weighted_choice_sub(m[s])
print(s)