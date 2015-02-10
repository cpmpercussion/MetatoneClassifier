"""
Testing Generation of Transition Matrices
2015-02-06
"""

import pandas as pd
import numpy as np
import transitions
from datetime import timedelta
from datetime import datetime

#from scipy.stats import entropy

## Make up some fake gesture data.

rng = pd.date_range(datetime.now(),periods = 35,freq = '1s')
columns = np.random.randint(0,9,(35,30))
data = pd.DataFrame(index = rng, data = columns)

transition_matrices = transitions.calculate_group_transitions_for_window(data,'15s')

latest_matrix = transition_matrices[-1]
entropy = transitions.entropy_measure(latest_matrix)
flux = transitions.flux_measure(latest_matrix)

print("\nLatest Matrix\n")
print(latest_matrix)
print("\nFlux: " + str(flux))
print("\nEntropy: " + str(entropy))

stochastic_matrix = transitions.transition_matrix_to_stochastic_matrix(latest_matrix)
entropy = transitions.entropy_measure(stochastic_matrix)
flux = transitions.flux_measure(stochastic_matrix)

print("\nReduced to stochastic:\n")
print(stochastic_matrix)
print("Flux: " + str(flux))
print("Entropy: " + str(entropy))

latest_matrix = transitions.reduce_matrix_to_groups(latest_matrix) # Reduce to Group Transitions.

entropy = transitions.entropy_measure(latest_matrix)
flux = transitions.flux_measure(latest_matrix)

print("\nLatest Matrix\n")
print(latest_matrix)
print("\nFlux: " + str(flux))
print("\nEntropy: " + str(entropy))

stochastic_matrix = transitions.transition_matrix_to_stochastic_matrix(latest_matrix)
entropy = transitions.entropy_measure(stochastic_matrix)
flux = transitions.flux_measure(stochastic_matrix)

print("\nReduced to stochastic:\n")
print(stochastic_matrix)
print("Flux: " + str(flux))
print("Entropy: " + str(entropy))


# group_transitions = group_transitions.resample(window_size,how=transition_sum)
