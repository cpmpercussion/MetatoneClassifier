from Cocoa import *
from Foundation import NSObject
import metatoneClassifier

class MetatoneClassifierController(NSWindowController):
    counterTextField = objc.IBOutlet()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)

        # Start the counter
        self.count = 0

    @objc.IBAction
    def increment_(self, sender):
        self.count += 1
        self.updateDisplay()

    @objc.IBAction
    def decrement_(self, sender):
        self.count -= 1
        self.updateDisplay()

    def updateDisplay(self):
        self.counterTextField.setStringValue_(self.count)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    viewController = MetatoneClassifierController.alloc().initWithWindowNibName_("MetatoneClassifierWindow")
    viewController.showWindow_(viewController)

    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)
    
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()