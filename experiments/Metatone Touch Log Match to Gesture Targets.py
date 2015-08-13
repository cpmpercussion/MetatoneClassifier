# Metatone Touch Experiments.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB

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
    fframe = pd.DataFrame({'freq':frame_freq,
        'device_id':frame['device_id'].resample(window_size,how='first')
            .fillna(method='ffill'),
        'touchdown_freq':frame_touchdowns.fillna(0),
        'movement_freq':frame_freq.fillna(0),
        'centroid_x':frame_centroid['x_pos'].fillna(-1),
        'centroid_y':frame_centroid['y_pos'].fillna(-1),
        'velocity':frame_vel.fillna(0)})
    return fframe.fillna(0)

##### Load some Data
##
##
#processed_file = open('/Users/charles/Dropbox/Metatone/20130504/20130504-set2-proctouches.txt','r')
processed_file = '/Users/charles/Dropbox/Metatone/20130701/OSCLog20130701-17h20m46s.txt-touches.csv'

# Gesture Targets
gestures_file = '/Users/charles/Dropbox/Metatone/20130701/MetatoneTargetGestures20130701-17h20m46s.csv-dateproc.csv'

messages = pd.read_csv(processed_file, index_col="time", parse_dates=True)
names = messages['device_id'].unique()

gesture_targets = pd.read_csv(gestures_file, index_col="time",parse_dates=True)
gesture_targets = gesture_targets.resample('5s',how='first')
gesture_targets = gesture_targets['charles']
gesture_targets.name = 'gesture'

## Classification Experiment

feature_vectors = pd.DataFrame()
for n in names:
    feature_vectors = pd.concat([feature_vectors, 
        feature_frame(messages.ix[messages['device_id'] == n])])
        
gnb = GaussianNB()

feature_vectors = feature_vectors[['centroid_x','centroid_y','freq','movement_freq','touchdown_freq','velocity']].join(gesture_targets)

sampler = np.random.randint(0, len(feature_vectors), size=50)
training_vectors = feature_vectors.take(sampler)

input_vectors = training_vectors[['centroid_x','centroid_y','freq','movement_freq','touchdown_freq','velocity']]
targets = training_vectors['gesture']

name_pred = gnb.fit(input_vectors, targets).predict(input_vectors)
print "Number of mislabeled points : %d" % (targets != name_pred).sum()
print "Accuracy: %f\%" % (targets != name_pred).sum() * 100 /len(targets)


name_pred = gnb.fit(input_vectors, targets).predict(feature_vectors[['centroid_x','centroid_y','freq','movement_freq','touchdown_freq','velocity']])
print "Number of mislabeled points from whole set : %d" % (feature_vectors['gesture'] != name_pred).sum()