import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import pickle

from sklearn.cross_validation import StratifiedKFold
import matplotlib.pyplot as plt

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



def pickleClassifier(file_name):
    """
    Trains a RandomForestClassifier and pickles the result
    """
    feature_vectors = pd.read_csv(file_name,index_col=0,parse_dates=True)
    feature_vectors = feature_vectors.rename(columns={'target':'gesture'})
    msk = np.random.rand(len(feature_vectors)) < TRAIN_PROPORTION
    train = feature_vectors[msk]
    test = feature_vectors[~msk]
    # build classifier
    classifier = RandomForestClassifier(n_estimators=100, max_features=3)
    classifier = classifier.fit(train[feature_vector_columns],train['gesture'])
    # score classifier
    mean_accuracy = classifier.score(test[feature_vector_columns],test['gesture'])
    print('Mean Accuracy:' + str(mean_accuracy) + '\n')
    # save pickled classifier
    pickle_file = open( file_name.replace('.csv','-classifier.p'), "wb" )
    pickle.dump(classifier, pickle_file)
    pickle_file.close()



def evaluateClassifier(classifier,feature_vectors):
    """
    Evaluates a classifier using a set of feature vectors and target gesture
    Evaluation is performed using Stratified 10-Fold cross validation and built in "score" function.
    Scores and stats are displayed.
    Scores returned as a numpy array.
    """
    ## Using stratified K-Folds validation
    vectors = np.array(feature_vectors[feature_vector_columns])
    targets = np.array(feature_vectors['gesture'])


    skf = StratifiedKFold(targets,10,shuffle=True)
    scores = np.array([])
    for train, test in skf:
        X_train, X_test, y_train, y_test = vectors[train], vectors[test], targets[train], targets[test]
        classifier.fit(X_train,y_train)
        s = classifier.score(X_test,y_test)
        #print("Score: " + str(s))
        scores = np.append(scores,s)
        # print(str(len(train)) + " " + str(len(test)))

    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    return scores

#from sklearn import cross_validation
#scores = cross_validation.cross_val_score(classifier,vectors,targets,cv=5)
#print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

##### Load some Data
##
data20130701_5s = '2013-07-01-TrainingData.csv' # 5s windowed data
data20130701_1s = '2013-07-01-TrainingData1s.csv' # 1s windowed data
data20141212_cpm = '2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv' # new processing collected data

data = [data20130701_5s,data20130701_1s,data20141212_cpm]
data_scores = []
tests = []
output = pd.DataFrame(index=pd.Series(range(100)))

for n in range(10):
    test = pd.DataFrame(index=pd.Series(range(10)))
    for f in data:
        print("Evaluating: " + f)
        classifier = RandomForestClassifier(n_estimators=100, max_features=3)
        feature_vectors = pd.read_csv(f,index_col=0,parse_dates=True)
        feature_vectors = feature_vectors.rename(columns={'target':'gesture'})
        scores = evaluateClassifier(classifier, feature_vectors)
        data_scores.append(scores)
        test = test.join(pd.DataFrame({f:scores}))
    tests.append(test)



output = pd.concat(tests,ignore_index=True)
output.columns = ['train2013-5s','train2013-1s','train2014-1s']

from scipy.stats import f_oneway
from scipy.stats import ttest_ind

print("Stats evaluations:")
aov = f_oneway(data_scores[0],data_scores[1],data_scores[2])
print("ANOVA: F:" + str(aov[0]) + " p:" + str(aov[1]))
print("Paired t-tests:")
t1 = ttest_ind(data_scores[0],data_scores[1])
t2 = ttest_ind(data_scores[1],data_scores[2])
t3 = ttest_ind(data_scores[0],data_scores[2])
print("0-1 " + str(t1))
print("1-2 " + str(t2))
print("0-2 " + str(t3))
