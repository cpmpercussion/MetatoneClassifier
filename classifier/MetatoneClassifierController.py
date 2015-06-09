# pylint: disable=line-too-long
"""
Controller Class for the Mac OS X GUI for Metatone Classifier.
"""
from __future__ import print_function
from Cocoa import *
from Foundation import NSObject
from AppKit import *
import metatoneClassifier
import threading, time
from datetime import datetime
import os
import shutil

class MetatoneClassifierController(NSWindowController):
    """
    Controller Class for Metatone Classifier GUI for Mac OS X. Uses the AppKit framework.
    """
    serverStatusLabel = objc.IBOutlet()
    activeDevicesLabel = objc.IBOutlet()
    ensembleTextField = objc.IBOutlet()
    performanceStateTextField = objc.IBOutlet()
    classifyingStatusLabel = objc.IBOutlet()
    lastClassificationTimeLabel = objc.IBOutlet()
    classifierWindow = objc.IBOutlet()
    startStopPerformanceButton = objc.IBOutlet()

    def __init__(self):
        """ Initialise the Classifier Controller """
        super(MetatoneClassifierController, self).__init__()
        self.classifying = False
        self.last_gesture_classes = "No performance started yet."
        self.last_performance_state = "No performance started yet."
        self.last_performance_time = ""
        self.current_active_devices = "None."
        self.current_performance_state = (False,False,False)
        self.classification_thread = threading.Thread(target=self.classify_forever, name="Classification-Thread")

    def windowDidLoad(self):
        """
        Runs after the window loads. Initialises the window elements in the pre-performance state.
        """
        NSWindowController.windowDidLoad(self)
        self.classifierWindow.setTitle_("Metatone Classifier")
        self.classifyingStatusLabel.setStringValue_("Not Classifying.")
        self.lastClassificationTimeLabel.setStringValue_("")
        self.startStopPerformanceButton.setTitle_("Start Performance!")
        self.classifying = False
        self.serverStatusLabel.setStringValue_("OSC Server Running. IP: " 
                                               + str(metatoneClassifier.receive_address[0]) 
                                               + " Port: " 
                                               + str(metatoneClassifier.receive_address[1]))
        self.activeDevicesLabel.setStringValue_(self.current_active_devices)


    @objc.IBAction
    def startStopPerformanceButtonPressed_(self, sender):
        """
        Alternates between the performance and stopped states.
        """
        if not self.classifying:
            self.start_performance()
        else:
            self.stop_performance()

    def start_performance(self):
        """
        Starts the performance state - starts a classification thread and sets it running.
        """
        print("Starting Classification!")
        # metatoneClassifier.startLog()
        if not self.classifying:
            self.classification_thread.start()
        self.classifyingStatusLabel.setStringValue_("Classifying...")
        self.startStopPerformanceButton.setTitle_("Stop Performance")

    def stop_performance(self):
        """
        Stops the performance state.
        """
        print("Stopping Classification.")
        if self.classifying:
            self.classifying = False
            self.classification_thread.join(2)
        self.classifyingStatusLabel.setStringValue_("Not Classifying.")
        self.startStopPerformanceButton.setTitle_("Start Performance")

    def update_display(self):
        """
        Updates the UI elements in the window.
        """
        self.ensembleTextField.setStringValue_(self.last_gesture_classes)
        self.performanceStateTextField.setStringValue_(self.last_performance_state)
        self.lastClassificationTimeLabel.setStringValue_(self.last_performance_time)
        self.current_active_devices = ""
        for name in metatoneClassifier.active_names:
            self.current_active_devices += name + ": "
            active_app = ""
            try:
                active_app = metatoneClassifier.active_apps[name]
            except:
                active_app = ""
            address = ("", 0)
            try:
                address = metatoneClassifier.osc_sources[name]
            except:
                address = ("", 0)
            self.current_active_devices += active_app + " "
            self.current_active_devices += str(address)
            self.current_active_devices += "\n" 
        self.activeDevicesLabel.setStringValue_(self.current_active_devices)

    def classify_forever(self):
        """
        Blocking server function that runs the classification step in the metatoneClassifier 
        until self.classifying is set to false.
        """
        self.classifying = True
        while self.classifying:
            time.sleep(1)
            self.current_performance_state = metatoneClassifier.classify_performance()
            metatoneClassifier.trim_touch_messages()
            self.update_performance_state()
            self.update_display()

    def update_performance_state(self):
        """
        Updates some of the UI elements related to data from the performance state
        of the metatoneClassifier.
        """
        self.last_performance_time = datetime.now().strftime("%H:%M:%S")
        self.last_gesture_classes = ""
        self.last_performance_state = ""
        classes = self.current_performance_state[0]
        state = self.current_performance_state[1]
        newidea = self.current_performance_state[2]
        if classes:
            self.last_gesture_classes = metatoneClassifier.pretty_print_classes(classes)
        if state:
            self.last_performance_state = metatoneClassifier.pretty_print_state(state)
        if newidea:
            self.last_performance_state += "\nNew Idea Detected!"

    @objc.IBAction
    def exportLogFiles_(self, sender):
        """
        Moves all saved logs to the desktop.
        Not working right! Currently has a hardcoded directory!
        """
        move_dir = "/Users/charles/Desktop/"
        logs_list = [n for n in os.listdir("logs") if n.endswith(".log")]
        for n in logs_list:
            shutil.move("logs/" + n, move_dir)
            shutil.move()
        metatoneClassifier.start_log()

    @objc.IBAction
    def openHelpUrl_(self, sender):
        NSWorkspace.sharedWorkspace().openURL_(NSURL.alloc().initWithString_("http://metatone.net/metatoneclassifier"))

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    # viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MainMenu")
    print("Loading Metatone Classifier.")
    metatoneClassifier.find_receive_address()
    metatoneClassifier.start_osc_server()
    metatoneClassifier.load_classifier()
    metatoneClassifier.start_log()
    print("Metatone Classifier Ready.")
    viewController.showWindow_(viewController)
    viewController.update_display()
    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()