import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle

##
## Setup Classifier
##

TRAIN_PROPORTION = 0.8 # uses this much of the full set for training, remainder for testing.

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

# file_name = "2013-07-01-TrainingData.csv" # 5s windowed data
#file_name = "2013-07-01-TrainingData1s.csv" # 1s windowed data
file_name = '2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv' # new processing collected data

feature_vectors = pd.read_csv(file_name,index_col=0,parse_dates=True)
feature_vectors = feature_vectors.rename(columns={'target':'gesture'})


msk = np.random.rand(len(feature_vectors)) < TRAIN_PROPORTION
train = feature_vectors[msk]
test = feature_vectors[~msk]



# take a sample of the data for training.
# sampler = np.random.randint(0, len(feature_vectors), size=len(feature_vectors))
# training_vectors = feature_vectors.take(sampler)
# input_vectors = np.asfortranarray(np.array(training_vectors[feature_vector_columns]))
# targets = np.asfortranarray(np.array(training_vectors['gesture']))

# input_vectors = np.asfortranarray(np.array(train[feature_vector_columns]))
# targets = np.asfortranarray(np.array(train['gesture']))

# Train the classifier
classifier = RandomForestClassifier(n_estimators=100, max_features=3)
# classifier = classifier.fit(input_vectors, targets)

classifier = classifier.fit(train[feature_vector_columns],train['gesture'])
# Test the classifier
mean_accuracy = classifier.score(test[feature_vector_columns],test['gesture'])

print('Mean Accuracy:' + str(mean_accuracy) + '\n')

## Save the classifier
pickle_file = open( file_name.replace('.csv','-classifier.p'), "wb" )
pickle.dump(classifier, pickle_file)
pickle_file.close()





## Using stratified K-Folds validation
from sklearn.cross_validation import StratifiedKFold

vectors = np.array(feature_vectors[feature_vector_columns])
targets = np.array(feature_vectors['gesture'])


skf = StratifiedKFold(targets,10,shuffle=True)
for train, test in skf:
    print(str(len(train)) + " " + str(len(test)))



from sklearn import cross_validation

scores = cross_validation.cross_val_score(classifier,vectors,targets,cv=5)
print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
