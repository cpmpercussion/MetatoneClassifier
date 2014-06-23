# Creates a Gesture Score (png file) from a Metatone Touch Log of the format:
# datetime, name, x_pos, y_pos, vel

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle
import argparse

#classifier_file = "20130701data-classifier.p"
classifier_file = "2013-07-01-TrainingData-classifier.p"
#classifier_file = "2013-07-01-TrainingData1s-classifier.p"


parser = argparse.ArgumentParser(description='Classify gestures from a Metatone Touch CSV with a CSV and PNG score output.')
parser.add_argument('filename',help='A Metatone Touch CSV file to be classified.')

args = parser.parse_args()

touchlog_file = args.filename

## Load the classifier
pickle_file = open( classifier_file, "rb" )
classifier = pickle.load(pickle_file)
pickle_file.close()

columns = ['time','device_id','x_pos','y_pos','velocity']
feature_vector_columns = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']

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

##### Function to calculate feature vectors 
## (for a dataframe containing one 'device_id'
##
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


##
##  Load up the next video data for Tests.
##
messages = pd.read_csv(touchlog_file, index_col="time", parse_dates=True)
names = messages['device_id'].unique()
gesture_pred = pd.DataFrame(messages['device_id'].resample('1s',how='count'))
ticks = gesture_pred.resample('10s').index.to_pydatetime()


# feature_vectors = pd.DataFrame()
# for n in names:
#     feature_vectors = pd.concat([feature_vectors, 
#         #feature_frame(messages.ix[messages['device_id'] == n])
#         generate_rolling_feature_frame(messages.ix[messages['device_id'] == n],n)
#         ])
        
# feature_vectors = feature_vectors[feature_vector_columns].join(gesture_targets)
# feature_vectors['gesture'] = feature_vectors['gesture'].fillna('N')


for n in names:
    performer_features = generate_rolling_feature_frame(messages.ix[messages['device_id'] == n],n)
    performer_features['pred'] = classifier.predict(performer_features[feature_vector_columns])
    gesture_pred[n] = performer_features['pred']
    print ("Processing Performer data for: " + n)

gesture_pred = gesture_pred.fillna(0)
gesture_pred = gesture_pred[names]
gesture_pred[names] = gesture_pred[names].astype(int)


# Create a good filename for the gesture score:
outname = gesture_pred.index[0].strftime('MetatoneAutoGestureScore%Y%m%d-%Hh%Mm%Ss')
performance_date = gesture_pred.index[0].strftime('%Y-%m-%d %H:%M:%S')

print ("Classification complete, saving output to CSV and PNG files named: " + outname)

# Save the gesture score as a CSV
gesture_pred.to_csv(outname + '.csv')

#Plot and save the Gesture Score as a png:
idx = gesture_pred.index
ax = plt.figure(figsize=(28,8),frameon=False,tight_layout=True).add_subplot(111)
ax.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0,30]))
ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
ax.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0,10,20,30,40,50]))
ax.xaxis.grid(True,which="minor")
ax.yaxis.grid()
 
plt.title("Automatically Generated Gesture Score for Performance: " + performance_date)
plt.ylabel("gesture")
plt.xlabel("time")
plt.ylim(-0.5,8.5)
plt.yticks(np.arange(9),['n','ft','st','fs','fsa','vss','bs','ss','c'])

for n in names:
    plt.plot_date(idx.to_pydatetime(),gesture_pred[n],'-',label=n)
plt.legend(loc='upper right')

plt.savefig(outname + '.png', dpi=150, format="png")
plt.close()