#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Calculates performance length in seconds for each member of a Metatone ensemble.
Performance length for each performer is defined as the time delta between the first touch in the performance and 
that performer''s final touch. 
The final touch may have to be adjusted due to accidental touches at the end of the log.
"""
from __future__ import print_function
import numpy as np
import pandas as pd


