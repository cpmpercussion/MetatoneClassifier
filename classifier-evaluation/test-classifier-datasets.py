
#dataset = '2013-07-01-TrainingData.csv'
dataset = '2013-07-01-TrainingData1s.csv'

feature_vectors = pd.read_csv(dataset, index_col=0, parse_dates=True)

## Testing Classification
samples = 10 #number of divisions in data
training_samples = []
test_samples = []
shuffled_points = range(len(feature_vectors))
np.random.shuffle(shuffled_points)
data_per_division = len(feature_vectors) / samples

for n in range(samples):
    test = shuffled_points[n*data_per_division:(n+1)*data_per_division]
    train = [x for x in shuffled_points if x not in test]
    training_samples.append(train)
    test_samples.append(test)

test_results = []

for n in range(samples):
    training_vectors = feature_vectors.take(training_samples[n])
    testing_vectors = feature_vectors.take(test_samples[n])
    training_targets = training_vectors['gesture']
    classifier = RandomForestClassifier(n_estimators=100,max_features=3,compute_importances=True)
    classifier = classifier.fit(training_vectors[feature_vector_columns],training_targets)
    # Testing
    test_results.append(classifier.score(testing_vectors[feature_vector_columns],testing_vectors['gesture']))

mean_acc = np.mean(test_results)

print('Mean accuracy: ' + str(mean_acc) +' Test Accuracies: '+ str(test_results))