from Cocoa import *
from Foundation import NSObject
from AppKit import *
import metatoneClassifier
import threading,time
from datetime import datetime
import os
import shutil

class MetatoneClassifierController(NSWindowController):
    serverStatusLabel = objc.IBOutlet()
    activeDevicesLabel = objc.IBOutlet()
    ensembleTextField = objc.IBOutlet()
    performanceStateTextField = objc.IBOutlet()
    classifyingStatusLabel = objc.IBOutlet()
    lastClassificationTimeLabel = objc.IBOutlet()
    classifierWindow = objc.IBOutlet()
    startStopPerformanceButton = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        self.classifierWindow.setTitle_("Metatone Classifier")
        self.lastGestureClasses = "No performance started yet."
        self.lastPerformanceState = "No performance started yet."
        self.lastPerformanceTime = ""
        self.classifyingStatusLabel.setStringValue_("Not Classifying.")
        self.lastClassificationTimeLabel.setStringValue_("")
        self.startStopPerformanceButton.setTitle_("Start Performance!")
        self.classifying = False
        self.serverStatusLabel.setStringValue_("OSC Server Running. IP: " + str(metatoneClassifier.receive_address[0]) 
            + " Port: " + str(metatoneClassifier.receive_address[1]))
        self.currentActiveDevices = "None."
        self.activeDevicesLabel.setStringValue_("None.")


    @objc.IBAction
    def startStopPerformanceButtonPressed_(self,sender):
        if not self.classifying:
            self.startPerformance()
        else:
            self.stopPerformance()

    def startPerformance(self):
        print("Starting Classification!")
        # metatoneClassifier.startLog()
        if not self.classifying:
            self.classificationThread = threading.Thread(target=self.classifyForever,name="Classification-Thread")
            self.classificationThread.start()
        self.classifyingStatusLabel.setStringValue_("Classifying...")
        self.startStopPerformanceButton.setTitle_("Stop Performance")

    def stopPerformance(self):
        print("Stopping Classification.")
        if self.classifying:
            self.classifying = False
            self.classificationThread.join(2)
        self.classifyingStatusLabel.setStringValue_("Not Classifying.")
        self.startStopPerformanceButton.setTitle_("Start Performance")

    def updateDisplay(self):
        self.ensembleTextField.setStringValue_(self.lastGestureClasses)
        self.performanceStateTextField.setStringValue_(self.lastPerformanceState)
        self.lastClassificationTimeLabel.setStringValue_(self.lastPerformanceTime)
        self.currentActiveDevices = ""
        for name in metatoneClassifier.active_names:
            self.currentActiveDevices += name + ": "
            app = ""
            try:
                app = metatoneClassifier.active_apps[name]
            except:
                app = ""
            address = ("",0)
            try:
                address = metatoneClassifier.osc_sources[name]
            except:
                address = ("",0)
            self.currentActiveDevices += app + " "
            self.currentActiveDevices += str(address)
            self.currentActiveDevices += "\n" 
        self.activeDevicesLabel.setStringValue_(self.currentActiveDevices)

    def classifyForever(self):
        self.classifying = True
        while (self.classifying):
            time.sleep(1)
            self.currentPerformanceState = metatoneClassifier.classifyPerformance()
            metatoneClassifier.trim_touch_messages()
            self.updatePerformanceState()
            self.updateDisplay()

    def updatePerformanceState(self):
        self.lastPerformanceTime = datetime.now().strftime("%H:%M:%S")
        self.lastGestureClasses = ""
        self.lastPerformanceState = ""
        classes = self.currentPerformanceState[0]
        state = self.currentPerformanceState[1]
        newidea = self.currentPerformanceState[2]
        if (classes):
            self.lastGestureClasses = metatoneClassifier.pretty_print_classes(classes)
        if (state):
            self.lastPerformanceState = metatoneClassifier.pretty_print_state(state)
        if (newidea):
            self.lastPerformanceState += "\nNew Idea Detected!"

    @objc.IBAction
    def exportLogFiles_(self,sender):
        movedir = "/Users/charles/Desktop/"
        logsList = [n for n in os.listdir("logs") if n.endswith(".log")]
        for n in logsList:
            shutil.move("logs/" + n,movedir)
            shutil.move()
        metatoneClassifier.startLog()

    @objc.IBAction
    def openHelpUrl_(self,sender):
        NSWorkspace.sharedWorkspace().openURL_(NSURL.alloc().initWithString_("http://metatone.net/metatoneclassifier"))

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    # viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MainMenu")
    print("Loading Metatone Classifier.")
    metatoneClassifier.findReceiveAddress()
    metatoneClassifier.startOscServer()
    metatoneClassifier.load_classifier()
    metatoneClassifier.startLog()
    print("Metatone Classifier Ready.")

    viewController.showWindow_(viewController)
    viewController.updateDisplay()

    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()