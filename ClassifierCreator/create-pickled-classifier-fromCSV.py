import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle

##
## Setup Classifier
##

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

##### Load some Data
##
##

# file_name = "2013-07-01-TrainingData.csv" # 5s windowed data
file_name = "2013-07-01-TrainingData1s.csv" # 1s windowed data

feature_vectors = pd.read_csv(file_name,index_col=0,parse_dates=True)


# take a sample of the data for training.
sampler = np.random.randint(0, len(feature_vectors), size=len(feature_vectors))
training_vectors = feature_vectors.take(sampler)
input_vectors = training_vectors[feature_vector_columns]
targets = training_vectors['gesture']

# Train the classifier
classifier = RandomForestClassifier(n_estimators=100, max_features=3,compute_importances=True)
classifier = classifier.fit(input_vectors, targets)

## Save the classifier
pickle_file = open( file_name.replace('.csv','-classifier.p'), "wb" )
pickle.dump(classifier, pickle_file)
pickle_file.close()
