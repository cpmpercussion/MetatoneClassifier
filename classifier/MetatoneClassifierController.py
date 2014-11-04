from Cocoa import *
from Foundation import NSObject
import metatoneClassifier
import threading,time

class MetatoneClassifierController(NSWindowController):
    ensembleTextField = objc.IBOutlet()
    performanceStateTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        print("Window Loaded")
        self.lastGestureClasses = "1 2 3 4"
        self.lastPerformanceState = "bla bla bla"

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
            try:
                time.sleep(1)
                metatoneClassifier.classifyPerformance()
                metatoneClassifier.trim_touch_messages()
            except:
                print("Couldn't Perform Classification - Exception.")
            # do the thing

    def stop_classifying(self):
        self.classifying = False


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
    print("Setting up the classifier")
    metatoneClassifier.findReceiveAddress()
    metatoneClassifier.startOscServer()
    metatoneClassifier.load_classifier()
    metatoneClassifier.startLog()



    viewController.showWindow_(viewController)
    print("Window Should be showing.")
    viewController.updateDisplay()

    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()