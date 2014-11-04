from Cocoa import *
from Foundation import NSObject
import metatoneClassifier

class MetatoneClassifierController(NSWindowController):
    ensembleTextField = objc.IBOutlet()
    performanceStateTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        ## do the stuff
        ## init the local objects
        print("Window Loaded")
        self.lastGestureClasses = ""
        self.lastPerformanceState = ""

    @objc.IBAction
    def startPerformance_(self,sender):
        print("Starting Performance!")
        ## do stuff

    @objc.IBAction
    def stopPerformance_(self,sender):
        print("Stopping Performance.")
        ## do more stuff.

    def updateDisplay(self):
        self.counterTextField.setStringValue_(self.count)
        self.ensembleTextField.setStringValue_(self.lastGestureClasses)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
    viewController.showWindow_(viewController)
    print("Window Should be showing.")

    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()