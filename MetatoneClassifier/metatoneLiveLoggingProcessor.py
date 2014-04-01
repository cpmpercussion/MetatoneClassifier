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
import transitions

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
    receive_address = ("107.170.207.234",port)


METATONE_RECEIVING_PORT = 51200

#NEW_IDEA_THRESHOLD = 0.3

# OSC Server. there are three different types of server. 
s = OSC.OSCServer(receive_address) # basic
##s = OSC.ThreadingOSCServer(receive_address) # threading
##s = OSC.ForkingOSCServer(receive_address) # forking
#s.addDefaultHandlers()

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
    print "\nStarting OSCServer. Use ctrl-C to quit."
    print "IP Address is: " + ip[0]
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
    '97F37307-2A95-4796-BAC9-935BF417AC42':'christina', # old
    '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne', # old
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan', #old
    'D346C530-BBC9-4C1E-9714-F17654BCC3BC':'yvonne', # new names
    '30CB5985-FC54-43FC-8B77-C8BE24AA443C':'charles', # new names
    'E9F60D46-EE37-489A-AD91-4ABC99E2BC80':'jonathan', # new names
    '35F73141-D3D5-4F00-9A28-EC5449A1A73D':'christina', #new names
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

## Active Device names:
active_names = []

## Function to calculate feature vectors 
## (for a dataframe containing one 'device_id'
def feature_frame(frame):
    ## Protection against empty dataframes
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

## Load the classifier
pickle_file = open( "20130701data-classifier.p", "rb" )
classifier = pickle.load(pickle_file)
pickle_file.close()

def classify_touch_messages(messages):
    if not messages:
        return None
    touch_frame = pd.DataFrame(messages,columns = ['time','device_id','x_pos','y_pos','velocity']) ## This line can fail with a ValueError exception
    touch_frame = touch_frame.set_index('time')
    delta = timedelta(seconds=-5)
    time_now = datetime.now()
    touch_frame = touch_frame.between_time((time_now + delta).time(), time_now.time())
    
    #names = touch_frame['device_id'].unique()
    classes = {}
    for n in active_names:
        features = feature_frame(touch_frame.ix[touch_frame['device_id'] == n])
        gesture = classifier.predict(features[feature_vector_columns][-1:])
        classes[n] = list(gesture)[0]
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
logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.txt"
logging_file = open("logs/"+logging_filename,'w')

def restart_log():
    live_messages = []
    touch_messages = []
    classified_gestures = []
    logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.txt"
    logging_file = open("logs/"+logging_filename,'w')

def close_log():
    write_log(live_messages)
    logging_file.close()

def log_messages(message,log):
    log.append(message)
    if (len(log) > 1000000):
        write_log(log)

def write_log(log):
    print("writing all the messages to disk!")
    output_messages = []
    for m in log:
        output_messages.append(str(m).replace("[","").replace("]","").replace("'","") + "\n")
    del live_messages[:]
    logging_file.writelines(output_messages)

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


def send_gestures(classes):
    class_names = ['n','ft','st','fs','fsa','vss','bs','ss','c']
    for n in osc_sources.keys():
        if n in classes.keys():
            msg = OSC.OSCMessage("/metatone/classifier/gesture")
            msg.extend([n,class_names[classes[n]]])
            try:
                oscClient.sendto(msg,osc_sources[n])
            except OSC.OSCClientError:
                print("Couldn't send message to " + name)
            except socket.error:
                print("Couldn't send message to " + name + ", bad address.")

## OSC Sending Methods

osc_sources = {}

def add_source_to_list(name,source):
    ## Addressing a dictionary.
    source_address = (source[0],METATONE_RECEIVING_PORT)
    if (name not in osc_sources.keys()):
        osc_sources[name] = source_address

def send_message_to_sources(msg):
    for name in osc_sources.keys():
        try:
            oscClient.sendto(msg,osc_sources[name])
            #print("Message sent to " + name)
        except OSC.OSCClientError:
            print("Couldn't send message to " + name)
        except socket.error:
            print("Couldn't send message to " + name + ", bad address.")
    log_line = [datetime.now().isoformat()]
    log_line.extend(msg)
    log_messages(log_line,live_messages)

def get_device_name(device_id):
    if device_id in device_names:
        return device_names[device_id]
    else:
        return device_id

def add_active_device(device_id):
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



s.addMsgHandler("/metatone/touch", touch_handler)
s.addMsgHandler("/metatone/touch/ended", touch_ended_handler)
s.addMsgHandler("/metatone/switch", switch_handler)
s.addMsgHandler("/metatone/online", onlineoffline_handler)
s.addMsgHandler("/metatone/offline", onlineoffline_handler)
s.addMsgHandler("/metatone/acceleration", accel_handler)
s.addMsgHandler("/metatone/app",metatone_app_handler)

print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
    print addr

# Start OSCServer
startOscServer()

##
## Run Loop
## Classifies all touch data every 1 second
## Ctrl-C closes server, thread and exits.
##
try :
    while 1 :
        try:
            time.sleep(1)
            try:
                classes = classify_touch_messages(touch_messages)
            except ValueError:
                print("Couldn't classify messages.")

            if (classes):
                send_gestures(classes)
                log_gestures(classes,classified_gestures)
                pretty_print_classes(classes)
                #print(current_transitions)
            gestures = make_gesture_frame(classified_gestures).fillna(0)
            current_transitions = transitions.calculate_transition_activity(gestures)
            
            state = transitions.current_transition_state(gestures)
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
        except KeyboardInterrupt:
            raise
        except:
            print("Couldn't perform analysis - exception")
except KeyboardInterrupt:
    print "\nClosing OSCServer."
    close_server()
    close_log()
    print "Closed."

# Metatone Message Structure
#
## Touch
## /metatone/touch sfff
## deviceID X Y vel
#
## Touch Ended
## /metatone/touch/ended s
## deviceID
#
## Switch
## /metatone/switch ssb
## deviceID switchname switchstate
#
## Online
## /metatone/online s s
## deviceID appID
#
## Offline
## /metatone/offline s
## deviceID
#
## Acceleration
## /metatone/acceleration sfff
## deviceID X Y Z
#

## TODO 2013-12-05 get it to go back to "n" when touches stop. Currently sits on most recent gesture.


## something like - 
## take the time now -
## select all entries that are within 5 seconds of now
