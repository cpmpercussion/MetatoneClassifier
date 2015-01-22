import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime


base_filename = "data/2014-12-12T12-05-53-GestureTargetLog-CPM"

# Load data
touches_filename = base_filename + "-touches.csv"
target_gestures_filename = base_filename + "-gesturetargets.csv"

gesture_targets = pd.read_csv(target_gestures_filename, index_col="time",parse_dates=True)
touches = pd.read_csv(touches_filename,index_col="time",parse_dates=True)



## Calculate Feature Vectors
FEATURE_VECTOR_COLUMNS = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']




def generate_rolling_feature_frame(messages,name):
	features = feature_frame(messages)
	features = features.resample('1s')
	features = features.apply(feature_vector_from_row_time,axis=1,frame=messages,name=name)
	return features

def feature_vector_from_row_time(row,frame,name):
	"""
	Takes a row from a dataframe of empty feature vectors.
	Returns ONE feature vector from the given dataframe before "time".
	"""
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

def feature_frame(frame):
	"""
	Calculates feature vectors for a dataframe of touch
	messages containing one device_id.
	"""
	if (frame.empty):
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

	window_size = '5s'
	count_zeros = lambda s: len([x for x in s if x==0])

	frame_deviceid = frame['device_id'].resample(window_size,how='first').fillna(method='ffill')
	frame_freq = frame['device_id'].resample(window_size,how='count').fillna(0)
	frame_touchdowns = frame['velocity'].resample(window_size,how=count_zeros).fillna(0)
	frame_vel = frame['velocity'].resample(window_size,how='mean').fillna(0)
	frame_centroid = frame[['x_pos','y_pos']].resample(window_size,how='mean').fillna(-1)
	frame_std = frame[['x_pos','y_pos']].resample(window_size,how='std').fillna(0)
	
	fframe = pd.DataFrame({
		'freq':frame_freq,
		'device_id':frame_deviceid,
		'touchdown_freq':frame_touchdowns,
		'movement_freq':frame_freq,
		'centroid_x':frame_centroid['x_pos'],
		'centroid_y':frame_centroid['y_pos'],
		'std_x':frame_std['x_pos'],
		'std_y':frame_std['y_pos'],
		'velocity':frame_vel})
	return fframe.fillna(0)


gesture_targets = gesture_targets.resample('1s',how='max')
name = touches["device_id"].unique()
feature_vectors = generate_rolling_feature_frame(touches,name)

feature_vectors = feature_vectors[FEATURE_VECTOR_COLUMNS].join(gesture_targets)


# cut out feature vectors already labelled as bad.
feature_vectors = feature_vectors[feature_vectors.target != 100]

# need to - 1. eliminate vectors where target is 100 (labelled as bad)
# 2. fix up vectors with no recorded touches (centroid_x == -1) and force them
# to be mapped to target 0 (i.e. nothing)
feature_vectors.ix[feature_vectors.centroid_x == -1,'target'] = 0

feature_vectors['target'].plot()

# test1 = feature_vectors[feature_vectors.centroid_x == -1]
# test2 = feature_vectors[feature_vectors.centroid_x == -1]

# now what's the next thing to do?

# 1. output to CSV.
