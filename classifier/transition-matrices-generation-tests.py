"""
Testing Generation of Transition Matrices
2015-02-06
"""

import pandas as pd
import numpy as np
import transitions
from datetime import timedelta
from datetime import datetime

from scipy.stats import entropy

## Make up some fake gesture data.

rng = pd.date_range(datetime.now(),periods = 35,freq = '1s')
columns = np.random.randint(0,9,(35,30))
data = pd.DataFrame(index = rng, data = columns)



transition_matrices = transitions.calculate_group_transitions_for_window(data,'15s')


# group_transitions = group_transitions.resample(window_size,how=transition_sum)
