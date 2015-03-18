import logging
import metatoneClassifier
import threading
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import OSC
import pybonjour
from datetime import timedelta
from datetime import datetime
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("name", default='MetatoneWebProc', help="name for webserver application", type=str)

METACLASSIFIER_SERVICE_TYPE = "_metatoneclassifier._tcp."
FAKE_OSC_IP_ADDRESS = '127.0.0.1'
FAKE_OSC_PORT = 9999
FAKE_OSC_SOURCE = (FAKE_OSC_IP_ADDRESS,FAKE_OSC_PORT)

#logger = logging.getLogger('gateway')

class Application(tornado.web.Application):
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
    def get(self):
        self.render("index.html")

connections = set()
clients = dict()

def processMetatoneMessageString(handler,time,packet):
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


def sendOSCToAllClients(address,arguments):
    print("Sending OSC to All Clients: " + repr(address) + repr(arguments))
    for connection in connections:
        try:
            connection.sendOSC(address,arguments)
        except:
            print("Exception sending group message to: " + connection.deviceID)

def sendOSCToIndividualClients(address,device_to_arg_dict):
    print("Sending OSC to Individual Clients: " + repr(address) + ' ' + repr(device_to_arg_dict))
    for connection in connections:
        if connection.deviceID in device_to_arg_dict.keys():
            try:
                connection.sendOSC(address,[connection.deviceID,device_to_arg_dict[connection.deviceID]])
            except:
                print("Exception sending individual message to: " + connection.deviceID)

##############################################

class MetatoneAppConnectionHandler(tornado.websocket.WebSocketHandler):
    deviceID = ''
    app = ''

    def open(self):
        print("Client opened WebSocket")
        connections.add(self)
        logging.info(datetime.now().isoformat() + " Connection Opened.")
        print("Connections: " + repr(connections))

    def on_message(self,message):
        time = datetime.now()
        processMetatoneMessageString(self,time,message)
            
    def on_close(self):
        print("Client closed WebSocket")
        logging.info(datetime.now().isoformat() + " Connection Closed.")
        connections.remove(self)

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
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', regtype)
        print('  domain  =', domain)

def main():
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
        bonjourServiceRegister.close()
        print("Closed down. Bye!")


if __name__ == "__main__":
    main()