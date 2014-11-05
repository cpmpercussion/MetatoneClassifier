from Cocoa import *
from Foundation import NSObject
from AppKit import *
import metatoneClassifier
import threading,time
from datetime import datetime

class MetatoneClassifierController(NSWindowController):
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

    @objc.IBAction
    def startStopPerformanceButtonPressed_(self,sender):
        if not self.classifying:
            self.startPerformance()
        else:
            self.stopPerformance()

    def startPerformance(self):
        print("Starting Classification!")
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