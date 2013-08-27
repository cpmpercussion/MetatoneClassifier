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

ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
#ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])


name    = "Metatone LiveProc"
port    = 9000
#receive_address = "10.0.1.2"
receive_address = (ip[0], port)

# OSC Server. there are three different types of server. 
s = OSC.OSCServer(receive_address) # basic
##s = OSC.ThreadingOSCServer(receive_address) # threading
##s = OSC.ForkingOSCServer(receive_address) # forking
#s.addDefaultHandlers()

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





##
## Setup Functions for Classifying Data
##
device_names = {
    '2678456D-9AE7-4DCC-A561-688A4766C325':'charles',
    '97F37307-2A95-4796-BAC9-935BF417AC42':'christina',
    '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne',
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan'}
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
    
##### Function to calculate feature vectors 
## (for a dataframe containing one 'device_id'
##
def feature_frame(frame):
    window_size = '5s'
    
    frame_freq = frame['device_id'].resample(window_size,how='count') 
    frame_touchdowns = frame.ix[frame['velocity'] == 0]
    frame_touchdowns = frame_touchdowns['velocity'].resample(window_size,how='count')
    frame_vel = frame['velocity'].resample(window_size,how='mean')
    frame_centroid = frame[['x_pos','y_pos']].resample(window_size,how='mean')
    frame_std = frame[['x_pos','y_pos']].resample(window_size,how='std')
    
    fframe = pd.DataFrame({'freq':frame_freq,
        'device_id':frame['device_id'].resample(window_size,how='first')
            .fillna(method='ffill'),
        'touchdown_freq':frame_touchdowns.fillna(0),
        'movement_freq':frame_freq.fillna(0),
        'centroid_x':frame_centroid['x_pos'].fillna(-1),
        'centroid_y':frame_centroid['y_pos'].fillna(-1),
        'std_x':frame_std['x_pos'].fillna(0),
        'std_y':frame_std['y_pos'].fillna(0),
        'velocity':frame_vel.fillna(0)})
    return fframe.fillna(0)

    

## Load the classifier
pickle_file = open( "20130701data-classifier.p", "rb" )
classifier = pickle.load(pickle_file)
pickle_file.close()

def classify_touch_messages(messages):
    if not messages:
        return {}

    touch_frame = pd.DataFrame(messages,columns = ['time','device_id','x_pos','y_pos','velocity'])
    touch_frame = touch_frame.set_index('time')
    
    names = touch_frame['device_id'].unique()
    classes = {}
    for n in names:
        features = feature_frame(touch_frame.ix[touch_frame['device_id'] == n])
        classes[n] = classifier.predict(features[feature_vector_columns][-1:])
    return classes

#import sched, time
#scheduler = sched.scheduler(time.time, time.sleep)
#def do_something(sc): 
#    print "Classifying"
#    print classify_touch_messages(touch_messages)
#    sc.enter(60, 1, do_something, (sc,))
#
#scheduler.enter(60, 1, do_something, (scheduler,))
#scheduler.run()


##
## Logging data functions
##
live_messages = []
touch_messages = []


logging_filename = datetime.now().isoformat().replace(":","-")[:19] + "-MetatoneOSCLog.txt"
logging_file = open(logging_filename,'w')

def log_messages(message,log):
    #print(message)
    log.append(message)
    if (len(log) > 1000):
        print("logging all the messages!")
        output_messages = []
        for m in log:
            output_messages.append(str(m).replace("[","").replace("]","").replace("'","") + "\n")
        # log it to disk
        del live_messages[:]
        logging_file.writelines(output_messages)
        # create a new live_messages

def write_log(log):
    print("logging all the messages!")
    output_messages = []
    for m in log:
        output_messages.append(str(m).replace("[","").replace("]","").replace("'","") + "\n")
    # log it to disk
    del live_messages[:]
    logging_file.writelines(output_messages)
    # create a new live_messages






##
## OSC Message Handling Functions
##

def touch_handler(addr, tags, stuff, source):
    if (tags == "sfff"):
        time = datetime.now()
        message = [time.isoformat(),"touch",device_names[stuff[0]],stuff[1],stuff[2],stuff[3]]
        log_messages(message,live_messages)
        touch_messages.append([time,device_names[stuff[0]],stuff[1],stuff[2],stuff[3]])
        
        
def touch_ended_handler(addr,tags,stuff,source):
    if (tags == "s"):
        message = [datetime.now().isoformat(),"touch/ended",device_names[stuff[0]]]
        log_messages(message,live_messages)

def switch_handler(addr,tags,stuff,source):
    print(tags)
    if (tags == "ssb"):
        message = [datetime.now().isoformat(),"switch",device_names[stuff[0]],stuff[1],stuff[2]]
        log_messages(message,live_messages)
        
def onlineoffline_handler(addr,tags,stuff,source):
    print(tags)
    if (tags == "s"):
        message = [datetime.now().isoformat(),addr,device_names[stuff[0]]]
        log_messages(message,live_messages)
        
def accel_handler(addr,tags,stuff,source):
    if (tags == "sfff"):
        #do nothing
        message = [datetime.now().isoformat(),"accel",device_names[stuff[0]],stuff[1],stuff[2],stuff[3]]
        #log_messages(message,live_messages)


s.addMsgHandler("/metatone/touch", touch_handler) # adding our function
s.addMsgHandler("/metatone/touch/ended", touch_ended_handler) # adding our function
s.addMsgHandler("/metatone/switch", switch_handler) # adding our function
s.addMsgHandler("/metatone/online", onlineoffline_handler) # adding our function
s.addMsgHandler("/metatone/offline", onlineoffline_handler) # adding our function
s.addMsgHandler("/metatone/acceleration", accel_handler) # adding our function

print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
    print addr

# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread(target = s.serve_forever)
st.start()

## For a given chunk of messages

## Divide into names
## calculate a feature frame

## if no data for a name - output 0

## otherwise output classifier(frame[0])

def close_server():
    # finish up.    
    sdRef.close()
    s.close()
    st.join()
    write_log(live_messages)
    logging_file.close()




##
## Run Loop
##
## Classifies all touch data every 1 second
##
## Ctrl-C closes server, thread and exits.
##
try :
    while 1 :
        time.sleep(1)
        print classify_touch_messages(touch_messages)
        # calculate latest classifications.

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    print "Waiting for Server-thread to finish"
    close_server()
    print "Done"




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
## /metatone/online s
## deviceID
#
## Offline
## /metatone/offline s
## deviceID
#
## Acceleration
## /metatone/acceleration sfff
## deviceID X Y Z
#


# {'charles': array([8])}
# {'charles': array([8])}
# OSCServer: KeyError on request from 10.0.0.52:57120: 'F'
# {'charles': array([8])}
# {'charles': array([8])}
# {'charles': array([8])}

