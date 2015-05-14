"""
Metatone Classifier Main File - Runs the classifier using a web socket.
Appropriate for local or remote server use.
"""
import logging
import metatoneClassifier
import threading
import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
import tornado.websocket
import os.path
import OSC
import pybonjour
from datetime import datetime
import random

define("port", default=8888, help="run on the given port", type=int)
define("name", default='MetatoneWebProc', help="name for webserver application", type=str)
define("type", default=0, help="Type of performance to start. 0 = Local, 1 = Remote, 2 = Both, 3 = None, 4 = Button, 5 = Server", type=int)

##
PERFORMANCE_TYPE_LOCAL = 0
PERFORMANCE_TYPE_REMOTE = 1
EXPERIMENT_TYPE_BOTH = 2
EXPERIMENT_TYPE_NONE = 3
EXPERIMENT_TYPE_BUTTON = 4
EXPERIMENT_TYPE_SERVER = 5
PERFORMANCE_TYPE_NAMES = [
    "Performane-Local", "Performance-Remote", "Experiment-Both", 
    "Experiment-None", "Experiment-Button", "Experiment-Server"]
##

METACLASSIFIER_SERVICE_TYPE = "_metatoneclassifier._tcp."
FAKE_OSC_IP_ADDRESS = '127.0.0.1'
FAKE_OSC_PORT = 9999
FAKE_OSC_SOURCE = (FAKE_OSC_IP_ADDRESS, FAKE_OSC_PORT)

#logger = logging.getLogger('gateway')

class Application(tornado.web.Application):
    """
    Main Application Class.
    """
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/classifier", MetatoneAppConnectionHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    """
    Handler class for web requests.
    """
    def get(self):
        self.render("index.html")

connections = set()
clients = dict()

def processMetatoneMessageString(handler, time, packet):
    message = OSC.decodeOSC(packet)
    try:
        if "/metatone/touch/ended" in message[0]:
            metatoneClassifier.touch_ended_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/touch" in message[0]:
            # def touch_handler(addr, tags, stuff, source):
            metatoneClassifier.touch_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/switch" in message[0]:
            metatoneClassifier.switch_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/online" in message[0]:
            metatoneClassifier.onlineoffline_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
            handler.sendOSC("/metatone/classifier/hello",[])
            handler.deviceID = message[2]
            handler.app = message[3]
        elif "/metatone/offline" in message[0]:
            metatoneClassifier.onlineoffline_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/acceleration" in message[0]:
            metatoneClassifier.accel_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/app" in message[0]:
            metatoneClassifier.metatone_app_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        elif "/metatone/targetgesture" in message[0]:
            metatoneClassifier.target_gesture_handler(message[0],message[1][1:],message[2:],FAKE_OSC_SOURCE)
        else:
            print("Got an unknown message! Address was: " + message[0])
            print u'Raw Message Data: {}'.format(packet)
    except():
        print("Message did not decode to a non-empty list.")


def sendOSCToAllClients(address, arguments):
    # print("Sending OSC to All Clients: " + repr(address) + repr(arguments))
    try:
        for connection in connections:
            try:
                connection.sendOSC(address,arguments)
            except:
                print("Exception sending group message to: " + connection.deviceID)
    except:
        print("Couldn't send group message. Probably clients still joining.")

def sendOSCToIndividualClients(address,device_to_arg_dict):
    # print("Sending OSC to Individual Clients: " + repr(address) + ' ' + repr(device_to_arg_dict))
    for connection in connections:
        if connection.deviceID in device_to_arg_dict.keys():
            try:
                connection.sendOSC(address,[connection.deviceID,device_to_arg_dict[connection.deviceID]])
            except:
                print("Exception sending individual message to: " + connection.deviceID)

def removeMetatoneAppFromClassifier(deviceID):
    print("!!!! Removing App: " + repr(deviceID))
    metatoneClassifier.remove_source(deviceID)

def clearMetatoneAppsFromClassifier():
    print("Clearing all apps from Classifier")
    metatoneClassifier.clear_all_sources()

##############################################

class MetatoneAppConnectionHandler(tornado.websocket.WebSocketHandler):
    deviceID = ''
    app = ''

    def open(self):
        print("Client opened WebSocket")
        connections.add(self)
        logging.info(datetime.now().isoformat() + " Connection Opened.")
        # print("Connections: " + repr(connections))

    def on_message(self,message):
        time = datetime.now()
        processMetatoneMessageString(self,time,message)
            
    def on_close(self):
        print("!!!! SERVER: Client closed WebSocket: " + self.deviceID)
        removeMetatoneAppFromClassifier(self.deviceID)
        logging.info(datetime.now().isoformat() + " Connection Closed, " + self.deviceID)
        connections.remove(self)
        print("!!!! Removal done.")

    def sendOSC(self,address,arguments):
        msg = OSC.OSCMessage(address)
        msg.extend(arguments)
        packet = msg.getBinary()
        try:
            self.write_message(packet,binary=True)
        except:
            logging.error("Error sending OSC message to client", exc_info=True)

##############################################

def bonjour_callback(sdRef, flags, errorCode, name, regtype, domain):
    """
    Callback function for bonjour service.
    """
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', regtype)
        print('  domain  =', domain)

def main():
    """
    Main function loads classifier and sets up bonjour service and web server.
    """
    global sdRef
    print("Loading Metatone Classifier.")
    metatoneClassifier.load_classifier()
    metatoneClassifier.startLog()
    print("Metatone Classifier Ready.")
    logging.info("WebServer Logging started - " + metatoneClassifier.logging_filename)
    print ("Classifier WebServer Started - logging to: " + metatoneClassifier.logging_filename)

    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    metatoneClassifier.name = options.name
    metatoneClassifier.performance_type = options.type
    logging.info("WebServer Performance type is: " + str(options.type) + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    print("WebServer Performance type is: " + str(options.type) + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    metatoneClassifier.performance_composition = random.randint(0,100)
    metatoneClassifier.WEB_SERVER_MODE = True
    metatoneClassifier.webserver_sendtoall_function = sendOSCToAllClients
    metatoneClassifier.webserver_sendindividual_function = sendOSCToIndividualClients

    classificationThread = threading.Thread(target=metatoneClassifier.classifyForever,name="Classification-Thread")

    print("Starting Bonjour Service.")
    bonjourServiceRegister = pybonjour.DNSServiceRegister(name = options.name,
                                     regtype = METACLASSIFIER_SERVICE_TYPE,
                                     port = options.port,
                                     callBack = bonjour_callback)
    
    try:
        classificationThread.start()
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("Received Ctrl-C - Closing down.")
        metatoneClassifier.stopClassifying()
        clearMetatoneAppsFromClassifier()
        bonjourServiceRegister.close()
        print("Closed down. Bye!")


if __name__ == "__main__":
    main()