#!/usr/bin/python
# pylint: disable=line-too-long
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
from __future__ import print_function
import pybonjour
import OSC
import time
import threading
import socket
from datetime import timedelta
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import logging
import transitions
import generate_classifier
import os
import random

##
SERVER_NAME = "MetatoneLiveProc"
SERVER_PORT = 9000
CLOUD_SERVER_IP = "107.170.207.234"

##
METATONE_RECEIVING_PORT = 51200
#NEW_IDEA_THRESHOLD = 0.3
# PICKLED_CLASSIFIER_FILE = '2013-07-01-TrainingData-classifier.p'
#PICKLED_CLASSIFIER_FILE = '2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors-classifier.p'
PICKLED_CLASSIFIER_FILE = 'classifier.p'
CLASSIFIER_TRAINING_FILE = "data/2014-12-12T12-05-53-GestureTargetLog-CPM-FeatureVectors.csv"
##
PERFORMANCE_TYPE_LOCAL = 0
PERFORMANCE_TYPE_REMOTE = 1
EXPERIMENT_TYPE_BOTH = 2
EXPERIMENT_TYPE_NONE = 3
EXPERIMENT_TYPE_BUTTON = 4
EXPERIMENT_TYPE_SERVER = 5
##
PERFORMANCE_TYPE = 4 #this can be 0-5
PERFORMANCE_COMPOSITION = 4 #this can be any random int.
PERFORMANCE_EVENT_NAME = "MetatonePerformanceStart"
##

##
VISUALISER_MODE_ON = True
VISUALISER_PORT = 61200
VISUALISER_HOST = 'localhost'
##

##
WEB_SERVER_MODE = False
##
classifying_forever = False
##

##
DEVICE_NAMES = {
    # '2678456D-9AE7-4DCC-A561-688A4766C325':'charles', # old
    # '95585C5C-C1C1-4612-9836-BFC68B0DC36F':'charles',
    # '97F37307-2A95-4796-BAC9-935BF417AC42':'christina', # old
    # '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne', # old
    # '2C4C4043-B7F7-4C22-B930-1472B1E18DBF':'yvonne',
    # '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan', #old
    # 'D346C530-BBC9-4C1E-9714-F17654BCC3BC':'yvonne', # new names
    # '30CB5985-FC54-43FC-8B77-C8BE24AA443C':'charles', # new names
    # 'E9F60D46-EE37-489A-AD91-4ABC99E2BC80':'jonathan', # new names
    # '00088B8E-D27C-4AE1-8102-5FE318589D3E':'jonathan',
    # '35F73141-D3D5-4F00-9A28-EC5449A1A73D':'christina', #new names
    # '8EEF3773-19CE-4F4D-99BB-2B5BC1CE460C':'christina', #14.07.10
    # '74C29BE8-6B34-4032-8E74-FCEC42DF3D5B':'christina',
    # '16742ED0-5061-4FC8-9BF6-6F23FF76D767':'charles_ipadair',
    # '0E98DD2F-94C2-45EE-BEC5-18718CA36D8B':'charles_ipadair',
    # '6EAD764A-E424-48EB-9672-03EF44679A5E':'iPad2-64-white',
    # '670EC230-5C3E-4759-B70F-5FDBCE14189B':'charles-iphone5'
}
##
# Column names for feature vectors.
FEATURE_VECTOR_COLUMNS = ['centroid_x', 'centroid_y', 'std_x', 'std_y', 'freq', 'movement_freq', 'touchdown_freq', 'velocity']
GESTURE_CLASS_NAMES = ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c']

######################################
#
# OSC UDP Server Functions. (Not used in webserver mode)
#
######################################

def bonjour_callback(service_reference, flags, error_code, name, reg_type, domain):
    """
    Callback function for bonjour service registration.
    """
    if error_code == pybonjour.kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', reg_type)
        print('  domain  =', domain)

def findReceiveAddress():
    """
    Figures out the local IP address and port that the OSCServer should use and
    starts the Bonjour service.
    """
    global name
    global port
    global receive_address
    global bonjour_service_register
    searched_ips = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
    #ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])
    # ip = socket.getaddrinfo(socket.gethostname(),9000)[:1][0][4]
    name = SERVER_NAME
    port = SERVER_PORT
    #receive_address = "10.0.1.2"
    try:
        receive_address = (searched_ips[0], port)
    except IndexError:
        if WEB_SERVER_MODE:
            print("Could not find IP address automatically. Using CLOUD_SERVER_IP in WEB_SERVER_MODE.")
            receive_address = (CLOUD_SERVER_IP, SERVER_PORT)
        else:
            print("Could not find IP address automatically. Using localhost instead.")
            receive_address = ("localhost", port)
    print("Server Address: " + str(receive_address))
    print("Starting Bonjour Service.")
    bonjour_service_register = pybonjour.DNSServiceRegister(name=name,
                                                            regtype="_osclogger._udp.",
                                                            port=port,
                                                            callBack=bonjour_callback)

def startOscServer():
    """
    Starts the OSCServer serving on a new thread and adds message handlers.
    """
    global server
    global server_thread
    print("Starting OSCServer.")
    # OSC Server. there are three different types of server. 
    server = OSC.OSCServer(receive_address) # basic
    server_thread = threading.Thread(target=server.serve_forever, name="OSC-Server-Thread")
    server_thread.start()
    # Add all the handlers.
    server.addMsgHandler("/metatone/touch", touch_handler)
    server.addMsgHandler("/metatone/touch/ended", touch_ended_handler)
    server.addMsgHandler("/metatone/switch", switch_handler)
    server.addMsgHandler("/metatone/online", onlineoffline_handler)
    server.addMsgHandler("/metatone/offline", onlineoffline_handler)
    server.addMsgHandler("/metatone/acceleration", accel_handler)
    server.addMsgHandler("/metatone/app", metatone_app_handler)
    server.addMsgHandler("/metatone/targetgesture", target_gesture_handler)

def close_server():
    """
    Closes the OSCServer, server thread and Bonjour service reference.
    """
    global server
    global server_thread
    global bonjour_service_register
    print("\nClosing OSC Server systems...")
    if 'bonjour_service_register' in globals() or 'bonjour_service_register' in locals():
        print("Closing Bonjour Service.")
        bonjour_service_register.close()
    if 'server' in globals() or 'server' in locals():
        print("Closing Server.")
        server.close()
    if 'server_thread' in globals() or 'server_thread' in locals():
        print("Closing Server Thread.")
        server_thread.join(1)
    print("Finished closing.")

def ensure_dir(file_name):
    """
    Checks if a directory exists in the local directory,
    if it doesn't, creates it.
    """
    dir_to_make = os.path.dirname(file_name)
    if not os.path.exists(dir_to_make):
        os.makedirs(dir_to_make)

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
    print("### Loading Gesture Classifier.           ###")
    try:
        pickle_file = open(PICKLED_CLASSIFIER_FILE, "rb")
        classifier = pickle.load(pickle_file)
        pickle_file.close()
        print("### Classifier file successfully loaded.  ###")
    except IOError:
        print("### IOError Loading Classifier.           ###")
        print("### Saving new pickled classifier object. ###")
        classifier = generate_classifier.pickleClassifier(generate_classifier.INPUT_FILE, generate_classifier.CLASSIFIER_NAME)
    except:
        print("### Exception Loading Classifier.         ###")
        print("### Generating new classifier object.     ###")
        classifier = generate_classifier.pickleClassifier(generate_classifier.INPUT_FILE, generate_classifier.CLASSIFIER_NAME)

#@profile
def feature_frame(frame):
    """
    Calculates feature vectors for a dataframe of touch
    messages containing one device_id.
    """
    if frame.empty:
        fframe = pd.DataFrame({
            'freq':pd.Series(0, index=range(1)),
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
    count_zeros = lambda s: len([x for x in s if x == 0])

    frame_deviceid = frame['device_id'].resample(window_size, how='first').fillna(method='ffill')
    frame_freq = frame['device_id'].resample(window_size, how='count').fillna(0)
    frame_touchdowns = frame['velocity'].resample(window_size, how=count_zeros).fillna(0)
    frame_vel = frame['velocity'].resample(window_size, how='mean').fillna(0)
    frame_centroid = frame[['x_pos', 'y_pos']].resample(window_size, how='mean').fillna(-1)
    frame_std = frame[['x_pos', 'y_pos']].resample(window_size, how='std').fillna(0)
    
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

#@profile
def classify_touch_messages(messages):
    """
    Given a list of touch messages, generates a gesture class
    for each active device for the preceding 5 seconds. 
    Returned as a dictionary.
    """
    if not messages:
        return classify_empty_touch_messages()
    touch_frame = pd.DataFrame(messages, columns=['time', 'device_id', 'x_pos', 'y_pos', 'velocity']) ## This line can fail with a ValueError exception
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

def make_gesture_frame(gesture_log):
    """
    Takes a log of gestures and returns a time series 
    with columns for each active device.
    """
    if not gesture_log:
        return pd.DataFrame(columns=['time'])
    gesture_columns = ['time']
    gesture_columns.extend(active_names)
    gesture_frame = pd.DataFrame(gesture_log, columns=gesture_columns).set_index('time')
    return gesture_frame

######################################
#
# Pretty-Printing Functions for terminal output.
#
######################################

def pretty_print_classes(classes):
    """
    Returns a string of each active device matched to a human
    readable gesture state.
    """
    names = list(classes)
    pretty_classes = {}
    result = ""
    for n in names:
        pretty_classes[n] = GESTURE_CLASS_NAMES[classes[n]]
        result += n + " : " + GESTURE_CLASS_NAMES[classes[n]] + "\n"
    # return pretty_classes
    return result

def pretty_print_state(state):
    """
    Returns a string of each part of the performance state
    labelled with its meaning.
    """
    result = "Transition Type: " + state[0] + "\n"
    result += "Spread: " + str(state[1]) + "\n"
    result += "Ratio: " + str(state[2])
    return result

######################################
#
# Logging data functions
#
######################################

def log_messages(message):
    """
    Log the message line to system log.
    """
    logging.info(str(message).replace("[", "").replace("]", "").replace("'", ""))

def record_latest_gestures(classes, global_gesture_log):
    """
    Given a dict of classes, adds them to the system log
    as well as the global list of gestures used for performance
    tracking.

    Also ensures that the global gesture list does not exceed 10 minutes of gestures.
    """
    if not classes:
        return
    current_time = datetime.now()
    ## First add to the file log.
    message_log_line = [current_time.isoformat()]
    message_log_line.append("/classifier/gestures")
    for key in classes.keys():
        message_log_line.append(key)
        message_log_line.append(classes[key])
    log_messages(message_log_line)
    
    ## Now add to the gesture log.
    ## TODO: add the whole classes dict! Not just the list of gestures! how stupid!
    classes = [classes[n] for n in classes.keys()]
    classes.insert(0, current_time)
    global_gesture_log.append(classes)

def trim_touch_messages():
    """
    Trims the global touch_messages list to the last five seconds of activity.
    """
    global touch_messages
    current_time = datetime.now()
    delta = timedelta(seconds=-5)
    touch_messages = [x for x in touch_messages if x[0] > current_time + delta]

MAX_GESTURE_LENGTH = 600

def trim_gesture_log():
    """
    Trims the global gesture list to the length defined in MAX_GESTURE_LENGTH. 
    This runs after every classification step.
    """
    global classified_gestures
    if len(classified_gestures) > MAX_GESTURE_LENGTH:
        classified_gestures = classified_gestures[:MAX_GESTURE_LENGTH]


######################################
#
# OSC sending Functions.
#
######################################

def send_gestures(classes):
    """
    Send gesture classes to the relevant active devices.
    """
    for n in osc_sources.keys():
        if n in classes.keys():
            msg = OSC.OSCMessage("/metatone/classifier/gesture")
            msg.extend([n, GESTURE_CLASS_NAMES[classes[n]]])
            try:
                oscClient.sendto(msg, osc_sources[n], timeout=10.0)
            except OSC.OSCClientError as err:
                print("Couldn't send gestures to " + n + ". OSCClientError")
                print(msg)
                print(err)
            except socket.error:
                print("Couldn't send gestures to " + n + ", bad address (removed).")
                remove_source(n)
    if WEB_SERVER_MODE:
        class_strings = {}
        for n in classes.keys():
            class_strings[n] = GESTURE_CLASS_NAMES[classes[n]]
        webserver_sendindividual_function("/metatone/classifier/gesture", class_strings)

def send_message_to_sources(msg):
    """
    Sends a message to all active devices.
    """
    for n in osc_sources.keys():
        try:
            oscClient.sendto(msg, osc_sources[n], timeout=10.0)
        except OSC.OSCClientError as err:
            print("Couldn't send message to " + n + ". OSCClientError")
            print(msg)
            print(err)
        except socket.error:
            print("Couldn't send message to " + n + ", bad address (removed).")
            remove_source(n)
    if WEB_SERVER_MODE:
        webserver_sendtoall_function(msg.address, msg.values())
    log_line = [datetime.now().isoformat()]
    log_line.extend(msg)
    log_messages(log_line)

## TODO - make sure these are working.
def send_performance_start_message(device_name):
    """
    Function to send an individual performance start message to a source.
    Should run when a source first connects.
    """
    msg = OSC.OSCMessage("/metatone/performance/start")
    msg.append(PERFORMANCE_EVENT_NAME)
    msg.append(device_name)
    msg.append(performance_type)
    msg.append(performance_composition)
    try:
        oscClient.sendto(msg, osc_sources[device_name], timeout=10.0)
    except OSC.OSCClientError as err:
        print("Couldn't send performance start to " + device_name + ". OSCClientError")
        print(msg)
        print(err)
    except socket.error:
        print("Couldn't send performance start to " + device_name + ", bad address (removed).")
        remove_source(osc_sources[device_name])
    if WEB_SERVER_MODE:
        # send to webclient
        webserver_sendtoall_function(msg.address, msg.values())
        # TODO - fix this up, need a new sending function on the webserver side.


## TODO - make sure these are working.
def send_performance_end_message(device_name):
    """
    Function to send an indivudal performance end message to source.
    """
    msg = OSC.OSCMessage("/metatone/performance/end")
    msg.append(PERFORMANCE_EVENT_NAME)
    msg.append(device_name)
    try:
        oscClient.sendto(msg, osc_sources[device_name], timeout=10.0)
    except OSC.OSCClientError as err:
        print("Couldn't send performance end to " + device_name + ". OSCClientError")
        print(msg)
        print(err)
    except socket.error:
        print("Couldn't send performance end to " + device_name + ", bad address (removed).")
        remove_source(osc_sources[device_name])
    if WEB_SERVER_MODE:
        webserver_sendtoall_function(msg.address, msg.values())
        # TODO - fix this up, need a new sending function on the webserver side.
    # send to webclient

def dummy_websocket_sender(address, arguments):
    """
    Dummy function: when running in webserver mode, the server replaces this with functions
    to send data to correct clients.
    """
    return
    # do nothing

def send_touch_to_visualiser(touch_data):
    """
    Sends touch data to the standard visualiser address.
    """
    msg = OSC.OSCMessage("/metatone/touch")
    msg.extend(touch_data)
    try: 
        oscClient.sendto(msg, (VISUALISER_HOST, VISUALISER_PORT))
    except:
        msg = ""

######################################
#
# Functions for keeping track of Metatone Clients.
#
######################################

def add_source_to_list(name, source):
    """
    Called whenever an OSC messaged is received.
    If a source is not listed, it's added to the dictionary,
    otherwise - nothing happens.
    """
    global osc_sources
    source_address = (source[0], METATONE_RECEIVING_PORT)
    if (name not in osc_sources.keys()):
        osc_sources[name] = source_address
        # send new performance start message.

def add_active_app(name, app):
    """
    Adds the current app whenever an online message is received.
    """
    global active_apps
    active_apps[name] = app

# TODO sort out this function so that it is useful - it should only be run inside the classification thread.
def remove_source(name):
    """
    Removes a device from the osc_sources dictionary. 
    Called after failing to contact the source.
    """
    global osc_sources
    global active_names
    # print("CLASSIFIER: Removing a source: " + name)
    # print("Sources: "+ repr(osc_sources))
    # print("Active Names: "+ repr(active_names))
    # if name in osc_sources: del osc_sources[name]
    # if name in active_names: active_names.remove(name) # can't do this until I fix gesture logging... needs to be dictionary not list. 

def clear_all_sources():
    """
    Sends a performance end message to all connected apps and then removes them all. 
    """
    global osc_sources
    global active_names
    global active_apps
    # send performance end messages.
    for name in osc_sources.keys():
        send_performance_end_message(name)
    osc_sources = {}
    active_names = []
    active_apps = []

def get_device_name(device_id):
    """
    Returns the device's name if known.
    This functionality needs work! Names shouldn't be hardcoded.
    """
    if device_id in DEVICE_NAMES:
        return DEVICE_NAMES[device_id]
    else:
        return device_id

def add_active_device(device_id):
    """
    Adds a device_name to the list if it isn't already on it.
    """
    device_name = get_device_name(device_id)
    if device_name not in active_names:
        active_names.append(device_name)



######################################
#
# OSC Message Handling Functions
#
######################################

def touch_handler(addr, tags, stuff, source):
    """ Handles /metatone/touch OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    if tags == "sfff":
        current_time = datetime.now()
        message = [current_time.isoformat(), "touch", get_device_name(stuff[0]), stuff[1], stuff[2], stuff[3]]
        log_messages(message)
        touch_messages.append([current_time, get_device_name(stuff[0]), stuff[1], stuff[2], stuff[3]])
        ## Repeat Message to visualiser:
        if VISUALISER_MODE_ON: 
            send_touch_to_visualiser(stuff)
        
def touch_ended_handler(addr, tags, stuff, source):
    """ Handles /metatone/touch/ended OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    if tags == "s":
        message = [datetime.now().isoformat(), "touch/ended", get_device_name(stuff[0])]
        log_messages(message)

def switch_handler(addr, tags, stuff, source):
    """ Handles /metatone/switch OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    if tags == "sss":
        message = [datetime.now().isoformat(), "switch", get_device_name(stuff[0]), stuff[1], stuff[2]]
        log_messages(message)
        
def onlineoffline_handler(addr, tags, stuff, source):
    """ Handles /metatone/online and /metatone/offline OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    send_performance_start_message(get_device_name(stuff[0]))
    if tags == "ss":
        message = [datetime.now().isoformat(), addr, get_device_name(stuff[0]), stuff[1]]
        print(get_device_name(stuff[0]) + " is online with " + stuff[1] + ".")
        add_active_app(get_device_name(stuff[0]), stuff[1])
        log_messages(message)
        
def accel_handler(addr, tags, stuff, source):
    """ Handles /metatone/acceleration OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    if tags == "sfff":
        # Just logs message - no action.
        message = [datetime.now().isoformat(), "accel", get_device_name(stuff[0]), stuff[1], stuff[2], stuff[3]]
        log_messages(message)

def metatone_app_handler(addr, tags, stuff, source):
    """ Handles /metatone/app OSC Messages """
    add_source_to_list(get_device_name(stuff[0]), source)
    add_active_device(stuff[0])
    if tags == "sss":
        message = [datetime.now().isoformat(), "metatone", get_device_name(stuff[0]), stuff[1], stuff[2]]
        log_messages(message)
        if WEB_SERVER_MODE:
            # Repeat message back to Metatone Devices.
            webserver_sendtoall_function(addr, stuff)

def target_gesture_handler(addr, tags, stuff, source):
    """ Handles /metatone/targetgesture OSC Messages """
    message = [datetime.now().isoformat(), addr, stuff[0]]
    # print("Capturing Target Gesture: " + str(stuff[0]))
    log_messages(message)

######################################
#
# Classification Loop Functions
#
######################################

#@profile
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
        if classes:
            send_gestures(classes)
            record_latest_gestures(classes, classified_gestures)
        gestures = make_gesture_frame(classified_gestures).fillna(0)
    except:
        print("Couldn't update gestures.")
        raise
    
    try:
        latest_gestures = transitions.trim_gesture_frame(gestures)
        transition_matrices = transitions.calculate_group_transitions_for_window(latest_gestures, '15s')
        flux_series = transitions.calculate_flux_series(transition_matrices)
        if isinstance(transition_matrices, pd.TimeSeries):
            state = transitions.transition_state_measure(transition_matrices[-1])
        else:
            state = False
    except:
        print ("Couldn't perform transition calculations.")
        state = False
        raise

    if state:
        # print(state)
        msg = OSC.OSCMessage("/metatone/classifier/ensemble/state")
        msg.extend([state[0], state[1], state[2]])
        send_message_to_sources(msg)
    newidea = transitions.is_new_idea(flux_series)
    if newidea:
        # print("New Idea Detected!")
        msg = OSC.OSCMessage("/metatone/classifier/ensemble/event/new_idea")
        msg.extend([name, "new_idea"])
        send_message_to_sources(msg)
    return (classes, state, newidea, flux_series)

def printPerformanceState(state_tuple):
    """
    Given the performance state tuple returned by classifyPerformance(),
    this function prints it out nicely on the screen.
    """
    print("# # # # # # # # # # # #")
    print("Classification: " + str(datetime.now()))
    classes = state_tuple[0]
    if classes:
        print(pretty_print_classes(classes))
    # state = state_tuple[1]
    # if state:
    #     print(pretty_print_state(state))
    # Print Flux Increase:
    flux_series = state_tuple[3]
    if isinstance(flux_series, pd.TimeSeries):
        flux_series = flux_series.dropna()
        if flux_series.count() > 0:
            flux_latest = flux_series.tolist()[-1]
            print("Latest flux reading: " + str(round(flux_latest, 3)))
        if flux_series.count() > 1:
            flux_diff = flux_series[-2:].diff().dropna().tolist()[0]
            print("Flux difference was: " + str(round(flux_diff)))
    newidea = state_tuple[2]
    if newidea:
        print("!! New Idea Detected !!")
    print("# # # # # # # # # # # #")

def classifyForever():
    """
    Starts a classification process that repeats every second.
    This blocks the thread.
    """
    global classifying_forever
    classifying_forever = True
    while classifying_forever:
        try:
            start_time = datetime.now()
            current_state = classifyPerformance()
            printPerformanceState(current_state)
            trim_touch_messages()
            trim_gesture_log()
            end_time = datetime.now()
            delta_seconds = (end_time-start_time).total_seconds() # process as timedelta
            print("(Classification took: " + str(delta_seconds) + "s)")
            print("Length of global gesture list: " + str(len(classified_gestures)) + "\n")
            time.sleep(max(0, 1-delta_seconds))
        except:
            print("### Couldn't perform analysis - exception. ###")
            raise

def stopClassifying():
    """
    Stops the classification process and also shuts down the server.
    """
    global classifying_forever
    classifying_forever = False
    time.sleep(1)
    clear_all_sources()
    close_server()

def startLog():
    """
    Start a new log with the filename set to the current time.
    Checks that we have a log directory and creates it if necessary.
    """
    global logging_filename
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging_filename = datetime.now().isoformat().replace(":", "-")[:19] + "-MetatoneOSCLog.log"
    logging.basicConfig(filename="logs/" + logging_filename, level=logging.DEBUG, format='%(message)s')
    logging.info("Logging started - " + logging_filename)
    print("Classifier Server Started - logging to: " + logging_filename)

######################################
#
# Main Function for running as a terminal application.
#
######################################

## Global Variables
osc_sources = {}
active_names = []
active_apps = {}
oscClient = OSC.OSCClient()
touch_messages = []
classified_gestures = []
receive_address = ("localhost",SERVER_PORT)
webserver_sendtoall_function = dummy_websocket_sender
webserver_sendindividual_function = dummy_websocket_sender
performance_type = PERFORMANCE_TYPE_LOCAL
performance_composition = random.randint(0,100)

def main():
    """
    Main Loop function used for terminal mode.
    Runs the clasifyForever function until it receives Ctrl-C
    at which point the program exits.
    """
    findReceiveAddress()
    startOscServer()
    load_classifier()
    startLog()

    try:
        classifyForever()
    except KeyboardInterrupt:
        print("\nReceived Ctrl-C - Closing down.")
        stopClassifying()
        print("Closed down. Bye!")

if __name__ == "__main__":
    main()
