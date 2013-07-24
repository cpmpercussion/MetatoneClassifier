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

ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])

name    = "Metatone LiveProc"
port    = 9000
receive_address = (ip[0], port)


# OSC Server. there are three different types of server. 
s = OSC.OSCServer(receive_address) # basic
##s = OSC.ThreadingOSCServer(receive_address) # threading
##s = OSC.ForkingOSCServer(receive_address) # forking
s.addDefaultHandlers()
# define a message-handler function for the server to call.

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


device_names = {
    '2678456D-9AE7-4DCC-A561-688A4766C325':'charles',
    '97F37307-2A95-4796-BAC9-935BF417AC42':'christina',
    '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne',
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan'}
columns = ['time','device_id','x_pos','y_pos','velocity']
live_messages = []


def touch_handler(addr, tags, stuff, source):
    if (tags == "sfff"):
        message = [datetime.now().isoformat(),device_names[stuff[0]],stuff[1],stuff[2],stuff[3]]
        live_messages.append(message)
        print(message)

s.addMsgHandler("/metatone/touch", touch_handler) # adding our function

print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
    print addr

# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = s.serve_forever )
st.start()

# finish up.    
sdRef.close()
s.close()
st.join()

# Working
def process_messages(messages):
   return 0
   
def calculate_featuers(messages):
    return 0
    
def classify_sample(sample):
    print 0 

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





