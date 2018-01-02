import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from generate_classifier import feature_frame
randn = np.random.randn

touch_messages = []


def fake_touch_handler():
    time = datetime.now()
    touch_messages.append([time, 'charles', randn() * 1024, randn() * 768, randn() * 100])


def classify_touch_messages(messages):
    touch_frame = pd.DataFrame(messages, columns=['time', 'device_id', 'x_pos', 'y_pos', 'velocity'])
    touch_frame = touch_frame.set_index('time')
    # return touch_frame
    # columns should be time, device_id, x_pos, y_pos, velocity
    names = touch_frame['device_id'].unique()

    classes = []

    for n in names:
        features = feature_frame(touch_frame.ix[touch_frame['device_id'] == n])
        classes.append([n, classifier(features[:1])])

    return classes


def make_data():
    for n in range(120):
        fake_touch_handler()

# Load the classifier
pickle_file = open("20130701data-classifier.p", "rb")
classifier = pickle.load(pickle_file)
pickle_file.close()
