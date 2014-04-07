import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle

## For iPython pretty printing.
pd.set_option('line_width',160)

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

## Newer version of feature_frame function
def feature_frame(frame):
    ## Protection against empty dataframes
    if (frame.empty):
        return zero_feature_vector()

    window_size = '5s'
    count_zeros = lambda s: len([x for x in s if x==0])
    count_nonzeros = lambda s: len([x for x in s if x!=0])

    frame_deviceid = frame['device_id'].resample(window_size,how='first').fillna(method='ffill')
    frame_freq = frame['device_id'].resample(window_size,how='count').fillna(0)
    frame_touchdowns = frame['velocity'].resample(window_size,how=count_zeros).fillna(0)
    frame_mvmt = frame['velocity'].resample(window_size,how=count_nonzeros).fillna(0)
    frame_vel = frame['velocity'].resample(window_size,how='mean').fillna(0)
    frame_centroid = frame[['x_pos','y_pos']].resample(window_size,how='mean').fillna(-1)
    frame_std = frame[['x_pos','y_pos']].resample(window_size,how='std').fillna(0)
    
    fframe = pd.DataFrame({
        'freq':frame_freq,
        'device_id':frame_deviceid,
        'touchdown_freq':frame_touchdowns,
        'movement_freq':frame_mvmt,
        'centroid_x':frame_centroid['x_pos'],
        'centroid_y':frame_centroid['y_pos'],
        'std_x':frame_std['x_pos'],
        'std_y':frame_std['y_pos'],
        'velocity':frame_vel})
    return fframe.fillna(0)

## Returns ONE feature vector from the given dataframe before "time"
def feature_vector_from_row_time(row,frame,name):
    time = row.name
    delta = timedelta(seconds=-5)
    frame = frame.between_time((time + delta).time(), time.time())
    if (frame.empty):
        return [-1,-1,name,0,0,0,0,0,0]
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_mvmt = frame.ix[frame['velocity'] != 0]
    frame_centroid = frame[['x_pos','y_pos']].mean()
    frame_std = frame[['x_pos','y_pos']].std().fillna(0)

    feature_vector = {
        'freq':frame['device_id'].count(),
        'device_id':name,
        'touchdown_freq':frame_touchdowns['device_id'].count(),
        'movement_freq':frame_mvmt['device_id'].count(),
        'centroid_x':frame_centroid[0],
        'centroid_y':frame_centroid[1],
        'std_x':frame_std[0],
        'std_y':frame_std[1],
        'velocity':frame['velocity'].mean()
    }
    return feature_vector

def zero_feature_row():
    fframe = pd.DataFrame({
            'freq':pd.Series(0,index=range(1)),
            'device_id':'nobody',
            'touchdown_freq':0,
            'movement_freq':0,
            'centroid_x':-1,
            'centroid_y':-1,
            'std_x':0,
            'std_y':0,
            'velocity':0})
    return fframe

def generate_rolling_feature_frame(messages,name):
    features = feature_frame(messages)
    features = features.resample('1s')
    features = features.apply(feature_vector_from_row_time,axis=1,frame=messages,name=name)
    return features


##### Load some Data
##
##
processed_file = '/Users/charles/Dropbox/Metatone/20130701/OSCLog20130701-17h20m46s.txt-touches.csv'
messages = pd.read_csv(processed_file, index_col="time", parse_dates=True)
names = messages['device_id'].unique()

# Gesture Targets
# gestures_file = '/Users/charles/Dropbox/Metatone/20130701/MetatoneTargetGestures20130701-17h20m46s.csv-dateproc.csv'
# gesture_targets = pd.read_csv(gestures_file, index_col="time",parse_dates=True)
# gesture_targets = gesture_targets.resample('1s',how='first')['charles']
# gesture_targets.name = 'gesture'
# gesture_targets = gesture_targets.fillna(method='ffill')

# New 1s file.
gestures_file = '2013-07-01-GestureTargets-1s.csv'
gesture_targets = pd.read_csv(gestures_file, index_col="time",parse_dates=True)
gesture_targets = gesture_targets['charles']
gesture_targets.name = 'gesture'
gesture_targets = gesture_targets.fillna(method='ffill')
gesture_targets = gesture_targets.apply(lambda x: gesture_codes[x])

##
## Setup Classifier with Synthetic Data 
##
# Setup the Data
feature_vectors = pd.DataFrame()
for n in names:
    feature_vectors = pd.concat([feature_vectors, 
        #feature_frame(messages.ix[messages['device_id'] == n])
        generate_rolling_feature_frame(messages.ix[messages['device_id'] == n],n)
        ])
        
feature_vectors = feature_vectors[feature_vector_columns].join(gesture_targets)
feature_vectors['gesture'] = feature_vectors['gesture'].fillna('N')
#feature_vectors['gesture'] = feature_vectors['gesture'].apply(lambda x: gesture_codes[x])

# Plotting:
# test = feature_vectors.copy()
# test['gesture'] = test['gesture'].apply(lambda x: 100*x)
# test.plot()


# Train the classifier on the whole set - ready to go.
classifier = RandomForestClassifier(n_estimators=100, max_features=3,compute_importances=True)
classifier = classifier.fit(feature_vectors[feature_vector_columns], feature_vectors['gesture'])

## Save the classifier
pickle_file = open( "20130701data-classifier.p", "wb" )
pickle.dump(classifier, pickle_file)
pickle_file.close()
