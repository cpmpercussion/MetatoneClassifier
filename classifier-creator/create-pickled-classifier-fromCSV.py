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
    'C': 8}

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
    folds = 10


    skf = StratifiedKFold(targets,folds,shuffle=True)
    scores = np.array([])
    confusion = np.zeros((9,9))
    for train, test in skf:
        X_train, X_test, y_train, y_test = vectors[train], vectors[test], targets[train], targets[test]
        classifier.fit(X_train,y_train)
        s = classifier.score(X_test,y_test)
        #print("Score: " + str(s))
        scores = np.append(scores,s)
        y_pred = classifier.predict(X_test)
        for x in range(len(y_test)):
            confusion[y_test[x]][y_pred[x]] = confusion[y_test[x]][y_pred[x]] + 1
        #c = confusion_matrix(y_test,y_pred)
        #print(str(len(train)) + " " + str(len(test)))
    confusion = confusion / 10.0
    #print("Confusion Matrix:\n" + str(confusion))
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    return scores, confusion

def plot_confusion_matrix(cm, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(gesture_codes))
    plt.xticks(tick_marks, gesture_codes)
    plt.yticks(tick_marks, gesture_codes)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

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
data_confusion_matrices = []
tests = []
confusions = {data20130701_5s:np.zeros((9,9)),data20130701_1s:np.zeros((9,9)),data20141212_cpm:np.zeros((9,9))}
output = pd.DataFrame(index=pd.Series(range(100)))



print("Testing Training Data...")

for n in range(10):
    test = pd.DataFrame(index=pd.Series(range(10)))
    test_confusions = pd.DataFrame(index=pd.Series(range(1)))
    for f in data:
        print("Evaluating: " + f)
        classifier = RandomForestClassifier(n_estimators=100, max_features=3)
        feature_vectors = pd.read_csv(f,index_col=0,parse_dates=True)
        feature_vectors = feature_vectors.rename(columns={'target':'gesture'})
        scores, confusion = evaluateClassifier(classifier, feature_vectors)
        data_scores.append(scores)
        confusions[f] = confusions[f] + confusion
        test = test.join(pd.DataFrame({f:scores}))
    tests.append(test)

for f in data:
    confusions[f] = confusions[f] / 10.0

print("Tests Complete.")


output = pd.concat(tests,ignore_index=True)
output.columns = ['train2013-5s','train2013-1s','train2014-1s']
# output_confusions = pd.concat(confusions,ignore_index=True)
# output_confusions.columns = ['train2013-5s','train2013-1s','train2014-1s']


# from scipy.stats import f_oneway
# from scipy.stats import ttest_ind

print("Stats evaluations:")
print("Not working right now, do it in R")
# aov = f_oneway(data_scores[0],data_scores[1],data_scores[2])
# print("ANOVA: F:" + str(aov[0]) + " p:" + str(aov[1]))
# print("Paired t-tests:")
# t1 = ttest_ind(data_scores[0],data_scores[1])
# t2 = ttest_ind(data_scores[1],data_scores[2])
# t3 = ttest_ind(data_scores[0],data_scores[2])
# print("0-1 " + str(t1))
# print("1-2 " + str(t2))
# print("0-2 " + str(t3))

plt.figure(figsize=(5.5,4),dpi=300)
plt.title("confusion matrix")
plt.imshow(mat, cmap=plt.cm.Blues, interpolation='nearest', vmin=0.0,vmax=1.0)
plt.colorbar() # shows the legend
labels =  ['N','FT','ST','FS','FSA','VSS','BS','SS','C']
plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8], labels)
plt.yticks([0, 1, 2, 3, 4], labels)
plt.savefig(filename.replace(":", "_") + '.pdf', dpi=300, format="pdf")
plt.close()
