import pandas as pd
import numpy as np
import transitions

# parser = argparse.ArgumentParser(description='Do something with a CSV file.')
# parser.add_argument('filename',help='A Metatone Gesture CSV file to be used.')
# args = parser.parse_args()
# gesture_file = args.filename

gesture_file = 'data/MetatoneAutoGestureScore20130803-18h38m11s.csv'
gestures = pd.read_csv(gesture_file, index_col='time', parse_dates=True)
transition_matrices = transitions.create_transition_dataframe(gestures)

group_matrix = transitions.calculate_group_transition_matrix(gestures)
## but this is the reduced gesture version... what about the full gesture version? probably need special transition algs.
