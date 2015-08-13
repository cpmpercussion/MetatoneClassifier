#! /usr/bin/env python
# pylint: disable=line-too-long
"""
Classifies Gestures from Metatone Touch Log at 1s intervals. Gestures are output as a CSV file and PDF plot.
datetime, name, x_pos, y_pos, vel
"""
from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import timedelta
import pickle
import argparse
import metatone_classifier

classifier = metatone_classifier.MetatoneClassifier()

##
## Pick whichever classifier you wish.
##
#classifier_file = "20130701data-classifier.p"
#classifier_file = "2013-07-01-TrainingData1s-classifier.p"
#classifier_file = "2013-07-01-TrainingData-classifier.p"

## Load the classifier
# pickle_file = open( classifier_file, "rb" )
# classifier = pickle.load(pickle_file)
# pickle_file.close()

#columns = ['time','device_id','x_pos','y_pos','velocity']

# ##### Function to calculate feature vectors
# ## (for a dataframe containing one 'device_id'
# ##
# ## Newer version of feature_frame function
# def feature_frame(frame):
#     ## Protection against empty dataframes
#     if (frame.empty):
#         return zero_feature_row()
#     window_size = '5s'
#     count_zeros = lambda s: len([x for x in s if x==0])
#     count_nonzeros = lambda s: len([x for x in s if x!=0])

#     frame_deviceid = frame['device_id'].resample(window_size,how='first').fillna(method='ffill')
#     frame_freq = frame['device_id'].resample(window_size,how='count').fillna(0)
#     frame_touchdowns = frame['velocity'].resample(window_size,how=count_zeros).fillna(0)
#     frame_mvmt = frame['velocity'].resample(window_size,how=count_nonzeros).fillna(0)
#     frame_vel = frame['velocity'].resample(window_size,how='mean').fillna(0)
#     frame_centroid = frame[['x_pos','y_pos']].resample(window_size,how='mean').fillna(-1)
#     frame_std = frame[['x_pos','y_pos']].resample(window_size,how='std').fillna(0)
    
#     fframe = pd.DataFrame({
#         'freq':frame_freq,
#         'device_id':frame_deviceid,
#         'touchdown_freq':frame_touchdowns,
#         'movement_freq':frame_mvmt,
#         'centroid_x':frame_centroid['x_pos'],
#         'centroid_y':frame_centroid['y_pos'],
#         'std_x':frame_std['x_pos'],
#         'std_y':frame_std['y_pos'],
#         'velocity':frame_vel})
#     return fframe.fillna(0)

# def zero_feature_row():
#     """
#     Returns a fake feature vector with one row of no touches.
#     """
#     fframe = pd.DataFrame({
#             'freq':pd.Series(0,index=range(1)),
#             'device_id':'nobody',
#             'touchdown_freq':0,
#             'movement_freq':0,
#             'centroid_x':-1,
#             'centroid_y':-1,
#             'std_x':0,
#             'std_y':0,
#             'velocity':0})
#     return fframe

def feature_vector_from_row_time(row, frame, name):
    """
    Returns ONE feature vector from the given dataframe before "time"
    """
    time = row.name
    delta = timedelta(seconds=-5)
    frame = frame.between_time((time + delta).time(), time.time())
    if frame.empty:
        return [-1, -1, name, 0, 0, 0, 0, 0, 0]
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_mvmt = frame.ix[frame['velocity'] != 0]
    frame_centroid = frame[['x_pos', 'y_pos']].mean()
    frame_std = frame[['x_pos', 'y_pos']].std().fillna(0)

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

def generate_rolling_feature_frame(messages, name):
    """
    Takes a message frame and creates a gesture frame with calculations every 1s.
    Returns the generated gesture frame.
    """
    features = metatone_classifier.feature_frame(messages)
    features = features.resample('1s')
    features = features.apply(feature_vector_from_row_time, axis=1, frame=messages, name=name)
    return features

def generate_gesture_frame(touchlog_frame):
    """
    Creates a dataframe of classified gestures at 1s intervals.
    """
    names = touchlog_frame['device_id'].unique()
    gesture_pred = pd.DataFrame(touchlog_frame['device_id'].resample('1s', how='count'))
    # ticks = gesture_pred.resample('10s').index.to_pydatetime()
    for name in names:
        print ("Processing Performer data for: " + name)
        performer_features = generate_rolling_feature_frame(touchlog_frame.ix[touchlog_frame['device_id'] == name], name)
        performer_features['pred'] = classifier.classifier.predict(performer_features[metatone_classifier.FEATURE_VECTOR_COLUMNS])
        gesture_pred[name] = performer_features['pred']
    gesture_pred = gesture_pred.fillna(0)
    gesture_pred = gesture_pred[names]
    gesture_pred[names] = gesture_pred[names].astype(int)
    return gesture_pred

def generate_gesture_plot(names, gesture_frame):
    """
    Probably a bad function for creating gesture plots
    """
    outname = gesture_frame.index[0].strftime('%Y-%m-%dT%H-%M-%S-MetatonePostHoc-gestures')
    performance_date = gesture_frame.index[0].strftime('%Y-%m-%d %H:%M:%S')
    idx = gesture_frame.index
    axes = plt.figure(figsize=(28, 8), frameon=False, tight_layout=True).add_subplot(111)
    axes.xaxis.set_major_locator(dates.SecondLocator(bysecond=[0, 30]))
    axes.xaxis.set_major_formatter(dates.DateFormatter("%H:%M:%S"))
    axes.xaxis.set_minor_locator(dates.SecondLocator(bysecond=[0, 10, 20, 30, 40, 50]))
    axes.xaxis.grid(True, which="minor")
    axes.yaxis.grid()
    plt.title("Post-hoc Gesture Score for Performance: " + performance_date)
    plt.ylabel("gesture")
    plt.xlabel("time")
    plt.ylim(-0.5, 8.5)
    plt.yticks(np.arange(9),['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    for name in names:
        plt.plot_date(idx.to_pydatetime(), gesture_frame[name], '-', label=name)
    plt.legend(loc='upper right')
    plt.savefig(outname + '.pdf', dpi=150, format="pdf")
    plt.close()

def main():
    """
    Takes a touch csv file as input, creates a gesture score csv and an image plot.
    """
    parser = argparse.ArgumentParser(description='Classifies Gestures from Metatone Touch Log at 1s intervals. Gestures are output as a CSV file and PDF plot.')
    parser.add_argument('filename', help='A Metatone Touch CSV file to be classified.')
    args = parser.parse_args()
    touchlog_file = args.filename
    print("Classifying Touch CSV file...")

    messages = pd.read_csv(touchlog_file, index_col="time", parse_dates=True)
    gesture_pred = generate_gesture_frame(messages)

    names = messages['device_id'].unique()
    generate_gesture_plot(names, gesture_pred)

    outname = gesture_pred.index[0].strftime('%Y-%m-%dT%H-%M-%S-MetatonePostHoc-gestures')
    gesture_pred.to_csv(outname + '.csv', date_format='%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':
    main()
