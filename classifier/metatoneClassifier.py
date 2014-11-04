#!/usr/bin/python
"""
metatoneClassifier Module

Copyright 2014 Charles Martin

http://metatone.net
http://charlesmartin.com.au

This file can be executed by itself (python metatoneClassifier.py) or used as a module 
by another python process.

If using as a module, call the main() function to initiate the normal run loop.

TODO:
- system for sending composition information to the connected iPads.
- system for holding messages that should be sent to each iPad that connects?
- better system for naming devices.
"""

import select
import sys
import pybonjour
import OSC
import time, threading
import socket
from datetime import timedelta
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import time,sched
import pickle
import logging
import transitions
import os

##
SERVER_NAME = "MetatoneLiveProc"
SERVER_PORT = 9000

##
METATONE_RECEIVING_PORT = 51200
#NEW_IDEA_THRESHOLD = 0.3
PICKLED_CLASSIFIER_FILE = '2013-07-01-TrainingData-classifier.p'
##

##
VISUALISER_MODE_ON = True
VISUALISER_PORT = 61200
VISUALISER_HOST = 'localhost'
##

##
WEB_SERVER_MODE = False
##

##
DEVICE_NAMES = {
	'2678456D-9AE7-4DCC-A561-688A4766C325':'charles', # old
	'95585C5C-C1C1-4612-9836-BFC68B0DC36F':'charles',
	'97F37307-2A95-4796-BAC9-935BF417AC42':'christina', # old
	'6769FE40-5F64-455B-82D4-814E26986A99':'yvonne', # old
	'2C4C4043-B7F7-4C22-B930-1472B1E18DBF':'yvonne',
	'1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan', #old
	'D346C530-BBC9-4C1E-9714-F17654BCC3BC':'yvonne', # new names
	'30CB5985-FC54-43FC-8B77-C8BE24AA443C':'charles', # new names
	'E9F60D46-EE37-489A-AD91-4ABC99E2BC80':'jonathan', # new names
	'00088B8E-D27C-4AE1-8102-5FE318589D3E':'jonathan',
	'35F73141-D3D5-4F00-9A28-EC5449A1A73D':'christina', #new names
	'8EEF3773-19CE-4F4D-99BB-2B5BC1CE460C':'christina', #14.07.10
	'74C29BE8-6B34-4032-8E74-FCEC42DF3D5B':'christina',
	'16742ED0-5061-4FC8-9BF6-6F23FF76D767':'charles_ipadair',
	'0E98DD2F-94C2-45EE-BEC5-18718CA36D8B':'charles_ipadair',
	'6EAD764A-E424-48EB-9672-03EF44679A5E':'iPad2-64-white',
	'670EC230-5C3E-4759-B70F-5FDBCE14189B':'charles-iphone5'
}
##

##
## Server Functions.
##
def bonjour_callback(sdRef, flags, errorCode, name, regtype, domain):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		print('Registered service:')
		print('  name    =', name)
		print('  regtype =', regtype)
		print('  domain  =', domain)

def findReceiveAddress():
	"""
	Figures out the local IP address and port that the OSCServer should use and
	starts the Bonjour service.
	"""
	global name
	global port
	global receive_address
	global sdRef
	ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
	#ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])
	name    = SERVER_NAME
	port    = SERVER_PORT
	#receive_address = "10.0.1.2"
	try:
		receive_address = (ip[0], port)
	except IndexError:
		if (WEB_SERVER_MODE):
			receive_address = ("107.170.207.234",port)
		else:
			receive_address = ("localhost",port)
	print("Server Address: " + str(receive_address))
	print("Starting Bonjour Service.")
	sdRef = pybonjour.DNSServiceRegister(name = name,
									 regtype = "_osclogger._udp.",
									 port = port,
									 callBack = bonjour_callback)

def startOscServer():
	"""
	Starts the OSCServer serving on a new thread and adds msg handlers.
	"""
	print("Starting OSCServer.")
	# OSC Server. there are three different types of server. 
	global s 
	s = OSC.OSCServer(receive_address) # basic
	##s = OSC.ThreadingOSCServer(receive_address) # threading
	##s = OSC.ForkingOSCServer(receive_address) # forking
	global st 
	st = threading.Thread(target = s.serve_forever, name="OSC-Server-Thread")
	st.start()
	# Add all the handlers.
	s.addMsgHandler("/metatone/touch", touch_handler)
	s.addMsgHandler("/metatone/touch/ended", touch_ended_handler)
	s.addMsgHandler("/metatone/switch", switch_handler)
	s.addMsgHandler("/metatone/online", onlineoffline_handler)
	s.addMsgHandler("/metatone/offline", onlineoffline_handler)
	s.addMsgHandler("/metatone/acceleration", accel_handler)
	s.addMsgHandler("/metatone/app",metatone_app_handler)

def close_server():
	"""
	Closes the OSCServer, server thread and Bonjour service reference.
	"""
	global s
	global st
	global sdRef
	print("\nClosing OSC Server and Bonjour Service.")
	sdRef.close()
	s.close()
	st.join(1)

def ensure_dir(f):
	"""
	Checks if a directory exists in the local directory,
	if it doesn't, creates it.
	"""
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

###########################
##
## Classification Functions
##
###########################

def load_classifier():
	"""
	Loads the pickled RandomForestClassifier object into 
	a global variable.
	"""
	global classifier
	pickle_file = open(PICKLED_CLASSIFIER_FILE, "rb" )
	classifier = pickle.load(pickle_file)
	pickle_file.close()

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

def classify_touch_messages(messages):
	"""
	Given a list of touch messages, generates a gesture class
	for each active device for the preceding 5 seconds. 
	Returned as a dictionary.
	"""
	FEATURE_VECTOR_COLUMNS = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']
	if not messages:
		return classify_empty_touch_messages()
	touch_frame = pd.DataFrame(messages,columns = ['time','device_id','x_pos','y_pos','velocity']) ## This line can fail with a ValueError exception
	touch_frame = touch_frame.set_index('time')
	delta = timedelta(seconds=-5)
	time_now = datetime.now()
	touch_frame = touch_frame.between_time((time_now + delta).time(), time_now.time())
	classes = {}
	for n in active_names:
		features = feature_frame(touch_frame.ix[touch_frame['device_id'] == n])
		gesture = classifier.predict(features[FEATURE_VECTOR_COLUMNS][-1:])
		classes[n] = list(gesture)[0]
	return classes

def classify_empty_touch_messages():
	"""
	Returns a valid classes dict with 0 in each value.
	Useful when there are no messages but active devices.
	"""
	classes = {}
	for n in active_names:
		classes[n] = 0
	return classes

def pretty_print_classes(classes):
	"""
	Prints classes to the terminal in a sort of pretty way.
	"""
	names = list(classes)
	class_names = ['n','ft','st','fs','fsa','vss','bs','ss','c']
	pretty_classes = {}
	for n in names:
		pretty_classes[n] = class_names[classes[n]]
	print(pretty_classes)

def make_gesture_frame(gesture_log):
	"""
	Takes a log of gestures and returns a time series 
	with columns for each active device.
	"""
	if not gesture_log:
		return pd.DataFrame(columns = ['time'])
	gesture_columns = ['time']
	gesture_columns.extend(active_names)
	gesture_frame = pd.DataFrame(gesture_log, columns = gesture_columns).set_index('time')
	return gesture_frame

##
## Logging data functions
##

def log_messages(message):
	"""
	Log the message line to system log.
	"""
	logging.info(str(message).replace("[","").replace("]","").replace("'",""))

def log_gestures(classes, log):
	"""
	Given a dict of classes, adds them to the system log
	as well as the global list of gestures used for performance
	tracking.
	"""
	if not classes:
		return
	time = datetime.now()
	## First add to the file log.
	message_log_line = [time.isoformat()]
	message_log_line.append("/classifier/gestures")
	for key in classes.keys():
		message_log_line.append(key)
		message_log_line.append(classes[key])
	log_messages(message_log_line)
	
	## Now add to the gesture log.
	classes = [classes[n] for n in classes.keys()]
	classes.insert(0,time)
	log.append(classes)

def trim_touch_messages():
	"""
	Trims the global touch_messages list to the last five seconds of activity.
	"""
	global touch_messages
	current_time = datetime.now()
	delta = timedelta(seconds=-5)
	touch_messages = [x for x in touch_messages if (x[0] > datetime.now() + delta)]

def send_gestures(classes):
	"""
	Send gesture classes to the relevant active devices.
	"""
	class_names = ['n','ft','st','fs','fsa','vss','bs','ss','c']
	for n in osc_sources.keys():
		if n in classes.keys():
			msg = OSC.OSCMessage("/metatone/classifier/gesture")
			msg.extend([n,class_names[classes[n]]])
			try:
				oscClient.sendto(msg,osc_sources[n],timeout=10.0)
			except OSC.OSCClientError as err:
				print("Couldn't send gestures to " + n + ". OSCClientError")
				print(msg)
				print(err)
			except socket.error:
				print("Couldn't send gestures to " + n + ", bad address (removed).")
				remove_source(n)

def send_message_to_sources(msg):
	"""
	Sends a message to all active devices.
	"""
	for n in osc_sources.keys():
		try:
			oscClient.sendto(msg,osc_sources[n],timeout=10.0)
		except OSC.OSCClientError as err:
			print("Couldn't send message to " + n + ". OSCClientError")
			print(msg)
			print(err)
		except socket.error:
			print("Couldn't send message to " + n + ", bad address (removed).")
			remove_source(n)
	log_line = [datetime.now().isoformat()]
	log_line.extend(msg)
	log_messages(log_line)

def send_touch_to_visualiser(touch_data):
	"""
	Sends touch data to the standard visualiser address.
	"""
	msg = OSC.OSCMessage("/metatone/touch")
	msg.extend(touch_data)
	try: 
		oscClient.sendto(msg,(VISUALISER_HOST,VISUALISER_PORT))
	except:
		msg = ""

def add_source_to_list(name,source):
	## Addressing a dictionary.
	global osc_sources
	source_address = (source[0],METATONE_RECEIVING_PORT)
	if (name not in osc_sources.keys()):
		osc_sources[name] = source_address

def remove_source(name):
	global osc_sources
	if name in osc_sources: del osc_sources[name]

def get_device_name(device_id):
	if device_id in DEVICE_NAMES:
		return DEVICE_NAMES[device_id]
	else:
		return device_id

def add_active_device(device_id):
	device_name = get_device_name(device_id)
	if device_name not in active_names:
		active_names.append(device_name)

##############################################
## OSC Message Handling Functions
##
def touch_handler(addr, tags, stuff, source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sfff"):
		time = datetime.now()
		message = [time.isoformat(),"touch",get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]]
		log_messages(message)
		touch_messages.append([time,get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]])
		## Repeat Message to visualiser:
		if (VISUALISER_MODE_ON): 
			send_touch_to_visualiser(stuff)
		
def touch_ended_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "s"):
		message = [datetime.now().isoformat(),"touch/ended",get_device_name(stuff[0])]
		log_messages(message)

def switch_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sss"):
		message = [datetime.now().isoformat(),"switch",get_device_name(stuff[0]),stuff[1],stuff[2]]
		log_messages(message)
		
def onlineoffline_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "ss"):
		message = [datetime.now().isoformat(),addr,get_device_name(stuff[0]),stuff[1]]
		print(get_device_name(stuff[0]) + " is online with "+stuff[1]+".")
		log_messages(message)
		
def accel_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sfff"):
		#do nothing
		message = [datetime.now().isoformat(),"accel",get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]]

def metatone_app_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sss"):
		message = [datetime.now().isoformat(),"metatone",get_device_name(stuff[0]),stuff[1],stuff[2]]
		log_messages(message)
##
##############################################

def classifyPerformance():
	"""
	Classifies the current performance state.
	Sends messages regarding current gestures, new ideas and other state.
	Designed to be used in a loop.
	"""
	global touch_messages
	global classified_gestures

	try:
		classes = classify_touch_messages(touch_messages)
	except:
		print("Couldn't classify messages.")
		classes = False
	try: 
		if (classes):
			send_gestures(classes)
			log_gestures(classes,classified_gestures)
			# pretty_print_classes(classes)
		gestures = make_gesture_frame(classified_gestures).fillna(0)
	except:
		print("Couldn't update gestures.")
		raise
	
	try:
		latest_gestures = transitions.trim_gesture_frame(gestures)
		current_transitions = transitions.calculate_transition_activity(latest_gestures)
		state = transitions.current_transition_state(latest_gestures)
	except:
		print ("Couldn't perform transition calculations.")
		state = False
		raise

	if (state):
		# print(state)
		msg = OSC.OSCMessage("/metatone/classifier/ensemble/state")
		msg.extend([state[0],state[1],state[2]])
		send_message_to_sources(msg)
	
	newidea = transitions.is_new_idea(current_transitions)
	if (newidea):
		# print("New Idea Detected!")
		msg = OSC.OSCMessage("/metatone/classifier/ensemble/event/new_idea")
		msg.extend([name,"new_idea"])
		send_message_to_sources(msg)

	return (classes,state,newidea)

def printPerformanceState(stateTuple):
	"""
	Given the performance state tuple returned by classifyPerformance(),
	this function prints it out nicely on the screen.
	"""
	print("# # # # # # # # # # # #")
	print("Performance State: " + str(datetime.now()))
	classes = stateTuple[0]
	state = stateTuple[1]
	newidea = stateTuple[2]
	if (classes):
		pretty_print_classes(classes)
	if (state):
		print(state)
	if (newidea):
		print("New Idea detected.")
	print("# # # # # # # # # # # #")


def classifyForever():
	"""
	Starts a classification process that repeats every second.
	This blocks the thread.
	"""
	global classifyingForever
	classifyingForever = True
	while classifyingForever:
		try:
			time.sleep(1)
			currentState = classifyPerformance()
			printPerformanceState(currentState)
			trim_touch_messages()
		except:
			print("Couldn't perform analysis - exception")
			raise

def stopClassifying():
	"""
	Stops the classification process and also shuts down the server.
	"""
	global classifyingForever
	classifyingForever = False
	time.sleep(1)
	close_server()

def startLog():
	"""
	Start a new log with the filename set to the current time.
	Checks that we have a log directory and creates it if necessary.
	"""
	if not os.path.exists('logs'):
		os.makedirs('logs')
	logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.log"
	logging.basicConfig(filename="logs/"+logging_filename,level=logging.DEBUG,format='%(message)s')
	logging.info("Logging started - " + logging_filename)
	print("Classifier Server Started - logging to: " + logging_filename)

## Global Variables
osc_sources = {}
active_names = []
oscClient = OSC.OSCClient()
touch_messages = []
classified_gestures = []

def main():
	"""
	Main Loop function used for terminal mode.
	"""
	findReceiveAddress()
	startOscServer()
	load_classifier()
	startLog()

	##
	## Run Loop
	## Classifies all touch data every 1 second
	## Ctrl-C closes server, thread and exits.
	##
	try:
		while True:
			try:
				time.sleep(1)
				currentState = classifyPerformance()
				printPerformanceState(currentState)
				trim_touch_messages()
			except KeyboardInterrupt:
				print("Received Ctrl-C - Closing down.")
				raise
			except:
				print("Couldn't perform analysis - exception")
				raise
	except KeyboardInterrupt:
		close_server()
		print("Closed down. Bye!")

if __name__ == "__main__":
	main()

# try:
# 	classes = classify_touch_messages(touch_messages)
# except:
# 	print("Couldn't classify messages.")
# try: 
# 	if (classes):
# 		send_gestures(classes)
# 		log_gestures(classes,classified_gestures)
# 		pretty_print_classes(classes)
# 	gestures = make_gesture_frame(classified_gestures).fillna(0)
# except:
# 	print("Couldn't update gestures.")
# 	raise

# try:
# 	latest_gestures = transitions.trim_gesture_frame(gestures)
# 	current_transitions = transitions.calculate_transition_activity(latest_gestures)
# 	state = transitions.current_transition_state(latest_gestures)
# except:
# 	print ("Couldn't perform transition calculations.")
# 	raise

# if (state):
# 	print(state)
# 	msg = OSC.OSCMessage("/metatone/classifier/ensemble/state")
# 	msg.extend([state[0],state[1],state[2]])
# 	send_message_to_sources(msg)

# if(transitions.is_new_idea(current_transitions)):
# 	print("New Idea Detected!")
# 	msg = OSC.OSCMessage("/metatone/classifier/ensemble/event/new_idea")
# 	msg.extend([name,"new_idea"])
# 	send_message_to_sources(msg)

# COLUMNS = ['time','device_id','x_pos','y_pos','velocity']
# GESTURE_CODES = {'N': 0,'FT': 1,'ST': 2,'FS': 3,'FSA': 4,
# 	'VSS': 5,'BS': 6,'SS': 7,'C': 8,'?': 9}