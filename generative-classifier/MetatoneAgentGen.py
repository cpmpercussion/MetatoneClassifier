## TODO: copy in relevant stuff from the MetatoneClassifier.
## Change timer so that every 1s it generates a new gesture for each player rather than classifies one.
## Otherwise -- everything else the same!

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
import random

## 1308 MetaLonsdale Ensemble Transition Matrix
TRANSITION_MATRIX = [[ 0.85245902,  0.00655738,  0.12459016,  0.00327869,  0.00655738,
		 0.        ,  0.        ,  0.00655738,  0.        ],
	   [ 0.00813008,  0.83739837,  0.14227642,  0.        ,  0.00406504,
		 0.00406504,  0.        ,  0.00406504,  0.        ],
	   [ 0.03225806,  0.02949309,  0.91612903,  0.01474654,  0.00645161,
		 0.        ,  0.        ,  0.00092166,  0.        ],
	   [ 0.        ,  0.04132231,  0.09090909,  0.63636364,  0.19834711,
		 0.00826446,  0.        ,  0.01652893,  0.00826446],
	   [ 0.01228501,  0.002457  ,  0.004914  ,  0.05405405,  0.84029484,
		 0.        ,  0.04422604,  0.02211302,  0.01965602],
	   [ 0.025     ,  0.        ,  0.025     ,  0.025     ,  0.        ,
		 0.775     ,  0.025     ,  0.05      ,  0.075     ],
	   [ 0.0060241 ,  0.        ,  0.        ,  0.0060241 ,  0.10240964,
		 0.0060241 ,  0.8373494 ,  0.03614458,  0.0060241 ],
	   [ 0.01123596,  0.        ,  0.03370787,  0.01123596,  0.07865169,
		 0.04494382,  0.06741573,  0.74157303,  0.01123596],
	   [ 0.00854701,  0.        ,  0.        ,  0.01709402,  0.05982906,
		 0.01709402,  0.01709402,  0.        ,  0.88034188]]

LAST_GESTURES = {}

def weighted_choice_sub(weights):
	rnd = random.random() * sum(weights)
	for i, w in enumerate(weights):
		rnd -= w
		if rnd < 0:
			return i

##
METATONE_RECEIVING_PORT = 51200
#NEW_IDEA_THRESHOLD = 0.3
##

##
VISUALISER_MODE_ON = True
VISUALISER_PORT = 61200
VISUALISER_HOST = 'localhost'
##

##
WEB_SERVER_MODE = False
##

## Global Variables
osc_sources = {}
active_names = []

##
## Set up OSC server and Bonjour Service
##
ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
#ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])

name    = "MetatoneLiveProc"
port    = 9000
#receive_address = "10.0.1.2"
try:
	receive_address = (ip[0], port)
except IndexError:
	if (WEB_SERVER_MODE):
		receive_address = ("107.170.207.234",port)
	else:
		receive_address = ("localhost",port)

# OSC Server. there are three different types of server. 
s = OSC.OSCServer(receive_address) # basic
##s = OSC.ThreadingOSCServer(receive_address) # threading
##s = OSC.ForkingOSCServer(receive_address) # forking

# Setup OSC Client.
oscClient = OSC.OSCClient()

##
## Register the Bonjour service
##
def register_callback(sdRef, flags, errorCode, name, regtype, domain):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		print 'Registered service:'
		print '  name    =', name
		print '  regtype =', regtype
		print '  domain  =', domain

sdRef = pybonjour.DNSServiceRegister(name = name,
									 regtype = "_osclogger._udp.",
									 port = port,
									 callBack = register_callback)

def startOscServer():
	print("\nStarting OSCServer. Use ctrl-C to quit.")
	print("IP Address is: " + receive_address[0])
	global st 
	st = threading.Thread(target = s.serve_forever)
	st.start()

def close_server():
	sdRef.close()
	s.close()
	st.join()

##
## Set up Functions for Classifying Data
##
device_names = {
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
	'6EAD764A-E424-48EB-9672-03EF44679A5E':'iPad2-64-white'
}

columns = ['time','device_id','x_pos','y_pos','velocity']
feature_vector_columns = ['centroid_x','centroid_y','std_x','std_y','freq','movement_freq','touchdown_freq','velocity']

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



def classify_touch_messages(messages):
	global TRANSITION_MATRIX
	global active_names
	if not messages:
		return classify_empty_touch_messages()
	classes = {}
	for n in active_names:
		try:
			classes[n] = weighted_choice_sub(TRANSITION_MATRIX[LAST_GESTURES[n]])
		except:
			classes[n] = 0
	return classes

def classify_empty_touch_messages():
	global active_names
	classes = {}
	for n in active_names:
		classes[n] = 0
	return classes

def pretty_print_classes(classes):
	names = list(classes)
	class_names = ['n','ft','st','fs','fsa','vss','bs','ss','c']
	pretty_classes = {}
	for n in names:
		pretty_classes[n] = class_names[classes[n]]
	print pretty_classes

def make_gesture_frame(gesture_log):
	if not gesture_log:
		return pd.DataFrame(columns = ['time'])
	gesture_columns = ['time']
	gesture_columns.extend(active_names)
	gesture_frame = pd.DataFrame(gesture_log, columns = gesture_columns).set_index('time')
	return gesture_frame

##
## Logging data functions
##
live_messages = []
touch_messages = []
classified_gestures = []

def log_messages(message,log):
	global logging
	logging.info(str(message).replace("[","").replace("]","").replace("'",""))

def log_message_new(message_list):
	global logging
	logging.info(str(message_list).replace("[","").replace("]","").replace("'",""))

def log_gestures(classes, log):
	if not classes:
		return
	time = datetime.now()
	## First add to the file log.
	message_log_line = [time.isoformat()]
	message_log_line.append("/classifier/gestures")
	for key in classes.keys():
		message_log_line.append(key)
		message_log_line.append(classes[key])
	log_messages(message_log_line,live_messages)
	
	## Now add to the gesture log.
	classes = [classes[n] for n in classes.keys()]
	classes.insert(0,time)
	log.append(classes)
	# log_message_new(message_list)


def send_gestures(classes):
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
	log_messages(log_line,live_messages)

def send_touch_to_visualiser(touch_data):
	msg = OSC.OSCMessage("/metatone/touch")
	msg.extend(touch_data)
	try: 
		oscClient.sendto(msg,(VISUALISER_HOST,VISUALISER_PORT))
	except:
		msg = ""
		# print("Can't send messsages to visualiser.")

def add_source_to_list(name,source):
	## Addressing a dictionary.
	global osc_sources
	## TODO: maybe have a dictionary of OSC clients connected to each iPad...
	## lets us use the best practice approach to sending messages to them.
	source_address = (source[0],METATONE_RECEIVING_PORT)
	if (name not in osc_sources.keys()):
		osc_sources[name] = source_address

def remove_source(name):
	global osc_sources
	if name in osc_sources: del osc_sources[name]



def get_device_name(device_id):
	if device_id in device_names:
		return device_names[device_id]
	else:
		return device_id

def add_active_device(device_id):
	global active_names
	device_name = get_device_name(device_id)
	if device_name not in active_names:
		active_names.append(device_name)

##
## OSC Message Handling Functions
##
def touch_handler(addr, tags, stuff, source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sfff"):
		time = datetime.now()
		message = [time.isoformat(),"touch",get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]]
		log_messages(message,live_messages)
		touch_messages.append([time,get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]])
		## Repeat Message to visualiser:
		if (VISUALISER_MODE_ON): 
			send_touch_to_visualiser(stuff)
		
def touch_ended_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "s"):
		message = [datetime.now().isoformat(),"touch/ended",get_device_name(stuff[0])]
		log_messages(message,live_messages)

def switch_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "sss"):
		message = [datetime.now().isoformat(),"switch",get_device_name(stuff[0]),stuff[1],stuff[2]]
		log_messages(message,live_messages)
		
def onlineoffline_handler(addr,tags,stuff,source):
	add_source_to_list(get_device_name(stuff[0]),source)
	add_active_device(stuff[0])
	if (tags == "ss"):
		message = [datetime.now().isoformat(),addr,get_device_name(stuff[0]),stuff[1]]
		print(get_device_name(stuff[0]) + " is online with "+stuff[1]+".")
		log_messages(message,live_messages)
		
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
		log_messages(message,live_messages)

def trim_touch_messages():
	# Only keeps the last five seconds of touch messages.
	# touch_messages.append([time,get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]])
	global touch_messages
	current_time = datetime.now()
	delta = timedelta(seconds=-5)
	touch_messages = [x for x in touch_messages if (x[0] > datetime.now() + delta)]

def main():
	s.addMsgHandler("/metatone/touch", touch_handler)
	s.addMsgHandler("/metatone/touch/ended", touch_ended_handler)
	s.addMsgHandler("/metatone/switch", switch_handler)
	s.addMsgHandler("/metatone/online", onlineoffline_handler)
	s.addMsgHandler("/metatone/offline", onlineoffline_handler)
	s.addMsgHandler("/metatone/acceleration", accel_handler)
	s.addMsgHandler("/metatone/app",metatone_app_handler)
	# print("Registered Callback-functions are :")
	# for addr in s.getOSCAddressSpace():
	#     print addr

	# Start OSCServer
	startOscServer()

	## Old Logging
	global live_messages
	global touch_messages
	global classified_gestures
	global logging_filename
	global logging_file

	# previous gestures for generator.
	global LAST_GESTURES

	## Better Logging
	global logger
	logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.log"
	logging.basicConfig(filename="logs/"+logging_filename,level=logging.DEBUG,format='%(message)s')
	logging.info("GenerativeAgent Logging started - " + logging_filename)
	print("GenerativeAgent Server Started - logging to: " + logging_filename)

	##
	## Run Loop
	## Classifies all touch data every 1 second
	## Ctrl-C closes server, thread and exits.
	##
	try :
		while 1 :
			try:
				time.sleep(1)
				#TODO: make sure there's a sensible answer if touch_messages is an empty list.
				try:
					classes = classify_touch_messages(touch_messages)
					LAST_GESTURES = classes
				except:
					print("Couldn't classify messages.")

				try: 
					if (classes):
						send_gestures(classes)
						log_gestures(classes,classified_gestures)
						pretty_print_classes(classes)
					gestures = make_gesture_frame(classified_gestures).fillna(0)
				except:
					print("Couldn't update gestures." + str(sys.exc_info()[0]))
				
				try:
					latest_gestures = transitions.trim_gesture_frame(gestures)
					current_transitions = transitions.calculate_transition_activity(latest_gestures)
					state = transitions.current_transition_state(latest_gestures)
				except:
					print ("Couldn't perform transition calculations.")

				if (state):
					print(state)
					msg = OSC.OSCMessage("/metatone/classifier/ensemble/state")
					msg.extend([state[0],state[1],state[2]])
					send_message_to_sources(msg)
				
				if(transitions.is_new_idea(current_transitions)):
					print "New Idea!\n"
					msg = OSC.OSCMessage("/metatone/classifier/ensemble/event/new_idea")
					msg.extend([name,"new_idea"])
					send_message_to_sources(msg)

				trim_touch_messages()
			except KeyboardInterrupt:
				raise # keep this raise!
			except:
				print("Couldn't perform analysis - exception: " + str(sys.exc_info()[0]))
				
	except KeyboardInterrupt:
		print "\nClosing OSCServer."
		close_server()
		print "Closed."

if __name__ == "__main__":
	main()