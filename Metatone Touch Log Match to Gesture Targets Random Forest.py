# Metatone Touch Experiments.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

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
    
def calculate_importances(forest,labels):
    importances = forest.feature_importances_
    std = np.std([tree.feature_importances_ for tree in classifier.estimators_],axis=0)
    indices = np.argsort(importances)[::-1]
    
    n = size(indices)
    # Print the feature ranking
    print "Feature ranking:"

    for f in xrange(n):
        print "%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]])

    # Plot the feature importances of the forest
    plt.figure()
    plt.title("Feature importances")
    plt.bar(xrange(n), importances[indices], color="r", yerr=std[indices], align="center")
    plt.xticks(xrange(n), [labels[x] for x in indices], rotation='vertical')
    plt.xlim([-1, n])
    plt.subplots_adjust(bottom=0.25)
    plt.show()

## Column names in the feature vectors:
feature_vector_columns = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']

class_groups = [[0],[1,2],[3,4,5],[6,7],[8],[9]]

def calculate_score(prediction,target):
    result = 5
    for n in class_groups:
        if ((prediction in n) and (target in n)):
            result = 1
        elif ((prediction in n) and not (target in n)):
            result = 3
    if (prediction == target):
        result = 0

    return result
            


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

##### Load some Data
##
##
processed_file = '/Users/charles/Dropbox/Metatone/20130701/OSCLog20130701-17h20m46s.txt-touches.csv'
messages = pd.read_csv(processed_file, index_col="time", parse_dates=True)

# Gesture Targets
gestures_file = '/Users/charles/Dropbox/Metatone/20130701/MetatoneTargetGestures20130701-17h20m46s.csv-dateproc.csv'
gesture_targets = pd.read_csv(gestures_file, index_col="time",parse_dates=True)
gesture_targets = gesture_targets.resample('5s',how='first')['charles']
gesture_targets.name = 'gesture'

# Setup columns and names.
names = messages['device_id'].unique()


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
calculate_importances(classifier, feature_vector_columns)


# Run a little experiment to check that it's working.
name_pred = classifier.predict(input_vectors)
print "Number of mislabeled points in training data : %d" % (targets != name_pred).sum()
print "Total points: %d" % len(targets)


name_pred = classifier.predict(feature_vectors[feature_vector_columns])
print "Number of mislabeled points from whole set : %d" % (feature_vectors['gesture'] != name_pred).sum()
print "Total points : %d" % len(feature_vectors['gesture'])
#print "Accuracy: %f\%" % (float(feature_vectors['gesture'] != name_pred).sum()) * 100 /len(feature_vectors['gesture'])

##
##  Load up the next video data for Tests.
##
touchlog_file = '/Users/charles/Dropbox/Metatone/20130427/MetatoneOSCLog-20130427-17h29.txt-touches.csv'
messages = pd.read_csv(touchlog_file, index_col="time", parse_dates=True)

# Gesture Targets
gesture_file = '/Users/charles/Dropbox/Metatone/20130427/MetatoneGesturesMicaiah-20130427-17h46m19s.csv-dateproc.csv'
gesture_targets = pd.read_csv(gesture_file, index_col="time",parse_dates=True)
gesture_targets = gesture_targets.resample('5s',how='first')

# Setup columns and names.
names = messages['device_id'].unique()

## Run an experiment: try the Classifier on each performer's touches.
print ""

#f, axarr = plt.subplots(size(names), sharex=True)


for n in names:
    performer_features = feature_frame(messages.ix[messages['device_id'] == n])
    performer_gestures = gesture_targets[n]
    performer_gestures.name = 'gesture'
    performer_features = performer_features[feature_vector_columns].join(performer_gestures)
    performer_features['gesture'] = performer_features['gesture'].apply(lambda x: gesture_codes[x])
    
    performer_pred = classifier.predict(performer_features[feature_vector_columns])
    performer_features['pred'] = classifier.predict(performer_features[feature_vector_columns])
    
    mean_accuracy = classifier.score(performer_features[feature_vector_columns],performer_features['gesture'])
    
    #axarr[names.tolist().index(n)] = 
    performer_features[['gesture','pred']].plot(title = n)
    
    scores = map(calculate_score,performer_pred.tolist(),performer_features['gesture'].tolist()) 
    
    print ("Processing Performer data for: " + n)
    print "Number of mislabeled points in Performer data : %d" % (performer_features['gesture'] != performer_pred).sum()
    print "Mean Accuracy: %f" % mean_accuracy
    print "Score: %d" % sum(scores)
    print "Total points: %d" % len(performer_features['gesture'])
    print ""


