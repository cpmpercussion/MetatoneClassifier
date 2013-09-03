# Creates a Gesture Score (png file) from a Metatone Touch Log of the format:
# datetime, name, x_pos, y_pos, vel

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from sklearn.ensemble import RandomForestClassifier
import pickle
import argparse


parser = argparse.ArgumentParser(description='Classify gestures from a Metatone Touch CSV with a CSV and PNG score output.')
parser.add_argument('filename',help='A Metatone Touch CSV file to be classified.')

args = parser.parse_args()

touchlog_file = args.filename

## Load the classifier
pickle_file = open( "20130701data-classifier.p", "rb" )
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


##
##  Load up the next video data for Tests.
##
#touchlog_file = '/Users/charles/Dropbox/Metatone/20130427/MetatoneOSCLog-20130427-17h29.txt-touches.csv'
#touchlog_file = '/Users/charles/Dropbox/Metatone/20130803/performance/OSCLog20130803-18h37m03s.txt-touches.csv'


messages = pd.read_csv(touchlog_file, index_col="time", parse_dates=True)
names = messages['device_id'].unique()
gesture_pred = pd.DataFrame(messages['device_id'].resample('5s',how='count'))

ticks = gesture_pred.resample('10s').index.to_pydatetime()

for n in names:
    performer_features = feature_frame(messages.ix[messages['device_id'] == n])
    
    #performer_features['pred'] = map(int,classifier.predict(performer_features[feature_vector_columns]))
    
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