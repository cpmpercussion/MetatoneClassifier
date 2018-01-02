#!/usr/bin/python
"""
Generates a Random Forest Classifier object to be used by the metatoneClassifier module.

Copyright 2014 Charles Martin

http://metatone.net
http://charlesmartin.com.au
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

# Old constants:
# PICKLED_CLASSIFIER_FILE = '2013-07-01-TrainingData-classifier.p'
# PICKLED_CLASSIFIER_FILE = '2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors-classifier.p'
# CLASSIFIER_TRAINING_FILE = "data/2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv"

CLASSIFIER_NAME = "classifier.p"
INPUT_FILE = "data/2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv"
TRAIN_PROPORTION = 1.0  # uses this much of the full set for training, remainder for testing.

# Int values for Gesture codes.
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

# Column names in the feature vectors:
feature_vector_columns = ['centroid_x', 'centroid_y', 'std_x', 'std_y', 'freq', 'movement_freq', 'touchdown_freq', 'velocity']

# Feature Vector Generation


def feature_frame(frame):
    """
    Calculates feature vectors for a dataframe of touch messages
    containing one device_id.
    """
    if frame.empty:
        fframe = pd.DataFrame({
            'freq': pd.Series(0, index=range(1)),
            'device_id': 'nobody',
            'touchdown_freq': 0,
            'movement_freq': 0,
            'centroid_x': -1,
            'centroid_y': -1,
            'std_x': 0,
            'std_y': 0,
            'velocity': 0})
        return fframe

    window_size = '5s'
    count_zeros = lambda s: len([x for x in s if x == 0])  # Count Zero.

    frame_deviceid = frame['device_id'].resample(window_size, how='first').fillna(method='ffill')
    frame_freq = frame['device_id'].resample(window_size, how='count').fillna(0)
    frame_touchdowns = frame['velocity'].resample(window_size, how=count_zeros).fillna(0)
    frame_vel = frame['velocity'].resample(window_size, how='mean').fillna(0)
    frame_centroid = frame[['x_pos', 'y_pos']].resample(window_size, how='mean').fillna(-1)
    frame_std = frame[['x_pos', 'y_pos']].resample(window_size, how='std').fillna(0)

    fframe = pd.DataFrame({
        'freq': frame_freq,
        'device_id': frame_deviceid,
        'touchdown_freq': frame_touchdowns,
        'movement_freq': frame_freq,
        'centroid_x': frame_centroid['x_pos'],
        'centroid_y': frame_centroid['y_pos'],
        'std_x': frame_std['x_pos'],
        'std_y': frame_std['y_pos'],
        'velocity': frame_vel})
    return fframe.fillna(0)


# Train Classifier from CSV of feature vectors


def trainClassifier(input_csv):
    """
    Trains a RandomForestClassifier and returns the result
    """
    try:
        feature_vectors = pd.read_csv(input_csv, index_col=0, parse_dates=True)
    except IOError:
        print("Trying one directory level higher...")
        feature_vectors = pd.read_csv("../" + input_csv, index_col=0, parse_dates=True)
    feature_vectors = feature_vectors.rename(columns={'target': 'gesture'})
    msk = np.random.rand(len(feature_vectors)) < TRAIN_PROPORTION
    train = feature_vectors[msk]
    test = feature_vectors[~msk]
    # build classifier
    classifier = RandomForestClassifier(n_estimators=100, max_features=3)
    classifier = classifier.fit(train[feature_vector_columns], train['gesture'])
    print('Classifier Trained. Testing...')
    print('Feature importances:' + str(classifier.feature_importances_))
    # score classifier
    if not test.empty:
        mean_accuracy = classifier.score(test[feature_vector_columns], test['gesture'])
        print('Mean Accuracy:' + str(mean_accuracy) + '\n')
    else:
        print("Can't test accuracy of classifier using whole dataset.")
    return classifier


# Save a trained classifier.


def pickleClassifier(input_csv, output_file):
    """
    Trains a RandomForestClassifier and pickles (and returns) the result
    """
    classifier = trainClassifier(input_csv)
    # save pickled classifier
    pickle_file = open(output_file, "wb")
    pickle.dump(classifier, pickle_file)
    pickle_file.close()
    return classifier


# Load a trained classifier or train automatically.classifier


def load_classifier():
    """
    Loads the pickled RandomForestClassifier object.
    """
    print("### Loading Gesture Classifier.           ###")
    try:
        pickle_file = open(CLASSIFIER_NAME, "rb")
        cla = pickle.load(pickle_file)
        pickle_file.close()
        print("### Classifier file successfully loaded.  ###")
    except IOError:
        print("### IOError Loading Classifier.           ###")
        print("### Saving new pickled classifier object. ###")
        cla = pickleClassifier(INPUT_FILE, CLASSIFIER_NAME)
    except:
        print("### Exception Loading Classifier.         ###")
        print("### Generating new classifier object.     ###")
        cla = pickleClassifier(INPUT_FILE, CLASSIFIER_NAME)
    return cla


# Some default script behaviour: Creates a default classifier.


if __name__ == "__main__":
    print("Creating Default Classifier File")
    classifier = pickleClassifier(INPUT_FILE, CLASSIFIER_NAME)
