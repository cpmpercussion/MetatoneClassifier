"""
Metatone Touch Experiments.
"""
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB

##### Function to calculate feature vectors 
## (for a dataframe containing one 'device_id'
##
def feature_frame(frame):
    """
    Calculate the feature vectors for a dataframe of touches.
    """
    window_size = '5s'
    
    
    frame_freq = frame['device_id'].resample(window_size, how='count') 
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_touchdowns = frame_touchdowns['velocity'].resample(window_size, how='count')
    frame_vel = frame['velocity'].resample(window_size, how='mean')
    frame_centroid = frame[['x_pos', 'y_pos']].resample(window_size, how='mean')
    
    
    fframe = pd.DataFrame({
        'freq':frame_freq,
        'device_id':frame['device_id'].resample(window_size, how='first').fillna(method='ffill'),
        'touchdown_freq':frame_touchdowns.fillna(0),
        'movement_freq':frame_freq.fillna(0),
        'centroid_x':frame_centroid['x_pos'].fillna(-1),
        'centroid_y':frame_centroid['y_pos'].fillna(-1),
        'velocity':frame_vel.fillna(0)})
    return fframe.fillna(0)

##### Load some Data
##
##
#PROCESSED_FILE = open('/Users/charles/Dropbox/Metatone/20130504/20130504-set2-proctouches.txt','r')
PROCESSED_FILE = '/Users/charles/Dropbox/Metatone/20130504/MetatoneOSCLog-20130504-14h23-touches.csv'

messages = pd.read_csv(PROCESSED_FILE, index_col="time", parse_dates=True)
names = messages['device_id'].unique()




## Count up the occurences of each device_id
#print(messages["device_id"].value_counts())
#counts = messages["device_id"].value_counts()
#counts.plot(kind='barh',rot=0)

#plt.scatter(messages["x_pos"],messages["y_pos"])

#plt.scatter(messages["x_pos"],messages["y_pos"],color='k',alpha=0.3)

#plt.scatter(messages["x_pos"],768-messages["y_pos"],color='k',alpha=0.05)
#plt.title('Density of touches in 20130504 Set 2')
#plt.axis([0,1024,0,768])

## Manually making some feature vectors....
charles_messages = messages.ix[messages['device_id'] == 'charles']
christina_messages = messages.ix[messages['device_id'] == 'christina']
yvonne_messages = messages.ix[messages['device_id'] == 'yvonne']
jonathan_messages = messages.ix[messages['device_id'] == 'jonathan']

charles_freq = charles_messages['device_id'].resample('2s',how='count')
christina_freq = christina_messages['device_id'].resample('2s',how='count')
yvonne_freq = yvonne_messages['device_id'].resample('2s',how='count')
jonathan_freq = jonathan_messages['device_id'].resample('2s',how='count')

freqs = pd.DataFrame({'charles_freq': charles_freq, 'christina_freq': christina_freq, 
'yvonne_freq':yvonne_freq, 'jonathan_freq':jonathan_freq})

totalfrequency = messages.resample('2s',how='count')
#totalfrequency.plot(kind='line',rot=0)


## Classification Experiment

feature_vectors = pd.DataFrame()
for n in names:
    feature_vectors = pd.concat([feature_vectors, 
        feature_frame(messages.ix[messages['device_id'] == n])])

gnb = GaussianNB()

sampler = np.random.randint(0, len(feature_vectors), size=100)
training_vectors = feature_vectors.take(sampler)

input_vectors = training_vectors[['centroid_x','centroid_y','freq','movement_freq','touchdown_freq','velocity']]
targets = training_vectors['device_id']

name_pred = gnb.fit(input_vectors, targets).predict(input_vectors)
print "Number of mislabeled points : %d" % (targets != name_pred).sum()
print "Accuracy: %f\%" % (targets != name_pred).sum() * 100 /len(targets)