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

##### Function to calculate feature vectors 
## (for a dataframe containing one 'device_id'
##
def feature_frame(frame):
    window_size = '5s'
    
    frame_freq = frame['device_id'].resample(window_size,how='count') 
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_touchdowns = frame_touchdowns['velocity'].resample(window_size,how='count')
    frame_vel = frame['velocity'].resample(window_size,how='mean')
    frame_centroid = frame[['x_pos','y_pos']].resample(window_size,how='mean')
    frame_std = frame[['x_pos','y_pos']].resample(window_size,how='std')
    
    fframe = pd.DataFrame({'freq':frame_freq,
        'device_id':frame['device_id'].resample(window_size,how='first')
            .fillna(method='ffill'),
        'touchdown_freq':frame_touchdowns.fillna(0),
        'movement_freq':frame_freq.fillna(0),
        'centroid_x':frame_centroid['x_pos'].fillna(-1),
        'centroid_y':frame_centroid['y_pos'].fillna(-1),
        'std_x':frame_std['x_pos'].fillna(0),
        'std_y':frame_std['y_pos'].fillna(0),
        'velocity':frame_vel.fillna(0)})
    return fframe.fillna(0)

##### Load some Data
##
##
processed_file = '/Users/charles/Dropbox/Metatone/20130701/OSCLog20130701-17h20m46s.txt-touches.csv'
messages = pd.read_csv(processed_file, index_col="time", parse_dates=True)
names = messages['device_id'].unique()

# Gesture Targets
gestures_file = '/Users/charles/Dropbox/Metatone/20130701/MetatoneTargetGestures20130701-17h20m46s.csv-dateproc.csv'
gesture_targets = pd.read_csv(gestures_file, index_col="time",parse_dates=True)
gesture_targets = gesture_targets.resample('5s',how='first')['charles']
gesture_targets.name = 'gesture'

##
## Setup Classifier with Synthetic Data 
##
# Setup the Data
feature_vectors = pd.DataFrame()
for n in names:
    feature_vectors = pd.concat([feature_vectors, 
        feature_frame(messages.ix[messages['device_id'] == n])])
        
feature_vectors = feature_vectors[feature_vector_columns].join(gesture_targets)
feature_vectors['gesture'] = feature_vectors['gesture'].fillna('N')
feature_vectors['gesture'] = feature_vectors['gesture'].apply(lambda x: gesture_codes[x])

# take a sample of the data for training.
sampler = np.random.randint(0, len(feature_vectors), size=len(feature_vectors))
training_vectors = feature_vectors.take(sampler)
input_vectors = training_vectors[feature_vector_columns]
targets = training_vectors['gesture']

# Train the classifier
classifier = RandomForestClassifier(n_estimators=100, max_features=3,compute_importances=True)
classifier = classifier.fit(input_vectors, targets)

## Save the classifier
pickle_file = open( "20130701data-classifier.p", "wb" )
pickle.dump(classifier, pickle_file)
pickle_file.close()
