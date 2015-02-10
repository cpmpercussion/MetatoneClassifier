#!/usr/bin/python
"""
Generates a Random Forest Classifier object to be used by the metatoneClassifier module.

Copyright 2014 Charles Martin

http://metatone.net
http://charlesmartin.com.au
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle

CLASSIFIER_NAME = "classifier.p"
INPUT_FILE = "data/2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv"
TRAIN_PROPORTION = 1.0 # uses this much of the full set for training, remainder for testing.

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

## Column names in the feature vectors:
feature_vector_columns = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']

def pickleClassifier(input_csv,output_file):
    """
    Trains a RandomForestClassifier and pickles the result
    """
    feature_vectors = pd.read_csv(input_csv,index_col=0,parse_dates=True)
    feature_vectors = feature_vectors.rename(columns={'target':'gesture'})
    msk = np.random.rand(len(feature_vectors)) < TRAIN_PROPORTION
    train = feature_vectors[msk]
    test = feature_vectors[~msk]
    # build classifier
    classifier = RandomForestClassifier(n_estimators=100, max_features=3)
    classifier = classifier.fit(train[feature_vector_columns],train['gesture'])
    # score classifier
    mean_accuracy = classifier.score(test[feature_vector_columns],test['gesture'])
    print('Mean Accuracy:' + str(mean_accuracy) + '\n')
    # save pickled classifier
    pickle_file = open(output_file, "wb" )
    pickle.dump(classifier, pickle_file)
    pickle_file.close()

if __name__ == "__main__":
    print("Creating Default Classifier File")
    pickleClassifier(INPUT_FILE,CLASSIFIER_NAME)
