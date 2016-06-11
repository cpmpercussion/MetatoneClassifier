import unittest
import transitions
import pandas as pd
import numpy as np
import random

class TransitionsTestCase(unittest.TestCase):
    """Tests for transitions module"""

    def test_reduced_transition_creation(self):
        m = transitions.empty_transition_matrix();
        self.assertTrue(isinstance(m,np.ndarray))
        self.assertTrue(sum(sum(m)) == 0) # test that's a zero matrix
        self.assertTrue(m.shape == (transitions.NUMBER_GROUPS,transitions.NUMBER_GROUPS))
    
    def test_one_step_transition(self):
        m = transitions.one_step_transition(random.randint(0,transitions.NUMBER_GROUPS),random.randint(0,transitions.NUMBER_GROUPS))
        self.assertTrue(isinstance(m,np.ndarray))
        self.assertTrue(sum(sum(m)) == 1)
        self.assertTrue(m.shape == (transitions.NUMBER_GROUPS,transitions.NUMBER_GROUPS))

    def test_flux_measure_zero_matrix(self):
        self.assertTrue(transitions.flux_measure(np.zeros((5,5))) == 0)

    def test_flux_measure_identity_matrix(self):
        m = np.identity(5)
        self.assertTrue(transitions.flux_measure(m) == 0)

    def test_flux_measure_no_diagonal(self):
        m = np.ones((5,5))
        n = np.identity(5)
        self.assertTrue(transitions.flux_measure(m - n) == 1)
    
if __name__ == '__main__':
    unittest.main()

