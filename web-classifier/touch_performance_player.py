"""Class for playing back sound objects on metatone apps."""
import OSC
import random
import pandas as pd
from threading import Timer

PLAYBACK_TOUCH_PATTERN = "/metatone/playback/touch"
PLAYBACK_GESTURE_PATTERN = "/metatone/playback/gesture"

class TouchPerformancePlayer:
    """Sends sound objects to an iPad for concatenative performance."""

    def __init__(self, name, address, port):
        self.client = OSC.OSCClient()
        self.performers = {}
        self.name = name
        self.address = (address,port)
        self.addPerformer(name,address,port)
        self.current_gesture = 0
        self.sound_objects = pd.DataFrame()
        self.timers = []
        self.empty_object = pd.DataFrame(columns = ["x","y","velocity","time"])
        self.available_gestures = [0]
        self.playing = False;
        print("Initialising a performance player for", name, "at", address + ":" + str(port))
        
    def setPerformances(self,sound_objects):
        """Set a dataframe of soundobjects for performances. DataFrame should have two column: objects and gestures"""
        self.sound_objects = sound_objects
        print("Setting up new sound_object dataframe:")
        print(self.sound_objects.gestures.value_counts())
        self.available_gestures = self.sound_objects.gestures.unique().tolist()
        self.available_gestures.append(0)
        print("Available Gestures:", self.available_gestures)

    def addPerformer(self, name, address, port):
        """Adds a performer's address and port to the list"""
        self.performers[name] = (address, port)
        
    def startPlaying(self):
        """Start sending sound objects to the performer."""
        if not self.playing:
            print("Starting Playback with gesture:", self.current_gesture)
            self.continuePlaying();
            
    def stopPlaying(self):
        """Stop sending sound objects to the performer and stop all timers."""
        if self.playing:
            print("Stopping playback and cancelling timers for:", self.name)
            self.cancelTimers()
            self.playing = False;
            self.current_gesture = 0;
        
    def continuePlaying(self):
        """Continue playing the gesture previously set."""
        print("Playing perf-object with gesture:", self.current_gesture, "on:", self.name)
        self.scheduleSoundObject(self.current_gesture)
        
    def updateGesture(self,new_gesture):
        """Update the gesture and start playing if it's different from before."""
        if self.current_gesture != new_gesture:
            # start playing new gesture immediately.
            self.current_gesture = new_gesture
            self.scheduleSoundObject(self.current_gesture)
    
    def cancelTimers(self):
        """Stop all current timers to send new performance objects."""
        for t in self.timers:
            t.cancel()
        self.timers = []
    
    def sendTouch(self, performer, x, y, velocity):
        """Sends an OSC message to trigger a touch sound."""
        address = self.performers[performer]
        self.client.sendto(OSC.OSCMessage(PLAYBACK_TOUCH_PATTERN, [performer,x, y, velocity]), address)
        
    def scheduleSoundObject(self,gesture):
        """Schedule a random sound object from a given gesture."""
        if gesture not in self.available_gestures:
            print("Sound object for gesture",gesture,"is not available.")
            return
        if gesture == 0:
            perf = self.empty_object
        else:
            perf = self.sound_objects[self.sound_objects.gestures == gesture].objects.sample(1)[0]
        self.schedulePerformance(perf,self.name)
        t = Timer(5.0,self.continuePlaying)
        self.timers.append(t)
        t.start()

    def schedulePerformance(self, perf, performer = "local"):
        """Schedule performance of a tiny performance dataframe."""
        self.cancelTimers()
        self.playing = True;
        if (perf.empty): # Returns if the perf is empty.
            return
        for row in perf.iterrows():
            self.timers.append(Timer(row[1]['time'],self.sendTouch,args=[performer,row[1]['x'],row[1]['y'],row[1]['velocity']]))
        for t in self.timers:    
            t.start()

# @"/metatone/playback/touch"
# 0: device
# 1: x
# 2: y
# 3: vel
# self.delegate didReceiveTouchPlayMessageFor:message.arguments[0] X:message.arguments[1] Y:message.arguments[2] vel:message.arguments[3]];

# @"/metatone/playback/gesture"
# 0: device
# 1: gesture class
# [self.delegate didReceiveGesturePlayMessageFor:message.arguments[0] withClass:message.arguments[1]];