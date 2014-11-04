from Cocoa import *
from Foundation import NSObject
import metatoneClassifier
import threading,time
from datetime import datetime

class MetatoneClassifierController(NSWindowController):
    ensembleTextField = objc.IBOutlet()
    performanceStateTextField = objc.IBOutlet()
    classifyingStatusLabel = objc.IBOutlet()
    classifyingSpinner = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        print("Window Loaded")
        self.lastGestureClasses = "1 2 3 4"
        self.lastPerformanceState = "bla bla bla"
        self.lastPerformanceTime = "None."

    @objc.IBAction
    def startPerformance_(self,sender):
        print("Starting Threaded Classification!")
        self.classificationThread = threading.Thread(target=self.classifyForever,name="Classification-Thread")
        self.classificationThread.start()

    @objc.IBAction
    def stopPerformance_(self,sender):
        print("Stopping Classification.")
        self.stop_classifying()
        self.classificationThread.join(2)

    def updateDisplay(self):
        self.ensembleTextField.setStringValue_(self.lastGestureClasses)
        self.performanceStateTextField.setStringValue_(self.lastPerformanceState)

    def classifyForever(self):
        self.classifying = True
        while (self.classifying):
            time.sleep(1)
            self.currentPerformanceState = metatoneClassifier.classifyPerformance()
            metatoneClassifier.trim_touch_messages()
            self.updatePerformanceState()
            self.updateDisplay()

    def stop_classifying(self):
        self.classifying = False

    def updatePerformanceState(self):
        self.lastPerformanceTime = str(datetime.now())
        self.lastGestureClasses = ""
        self.lastPerformanceState = ""
        classes = self.currentPerformanceState[0]
        state = self.currentPerformanceState[1]
        newidea = self.currentPerformanceState[2]
        if (classes):
            self.lastGestureClasses = str(classes)
            # pretty_print_classes(classes)
        if (state):
            self.lastPerformanceState = str(state)
        if (newidea):
            self.lastPerformanceState += "\nNew Idea detected."

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
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