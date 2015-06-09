# pylint: disable=line-too-long
"""
Metatone Classifier Main File - Runs the classifier using a web socket.
Appropriate for local or remote server use.
"""
from __future__ import print_function
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

class MetatoneWebApplication(tornado.web.Application):
    """
    Main Web Application Class.
    """
    connections = set()
    clients = dict()

    def __init__(self):
        handlers = [
            (r"/", MetatoneWebsiteHandler),
            (r"/classifier", MetatoneAppConnectionHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

    def send_osc_to_all_clients(self, address, arguments):
        """
        Sends an OSC formatted message with the same contents to all
        clients.
        """
        # print("Sending OSC to All Clients: " + repr(address) + repr(arguments))
        try:
            for connection in self.connections:
                try:
                    connection.send_osc(address, arguments)
                except:
                    print("Exception sending group message to: " + connection.deviceID)
        except:
            print("Couldn't send group message. Probably clients still joining.")

    def send_osc_to_individual_clients(self, address, device_to_arg_dict):
        """
        Sends an OSC formatted message with the same address to each
        connected client according to the dictionary of arguments.
        """
        # print("Sending OSC to Individual Clients: " + repr(address) + ' ' + repr(device_to_arg_dict))
        for connection in self.connections:
            if connection.deviceID in device_to_arg_dict.keys():
                try:
                    connection.send_osc(address, [connection.deviceID, device_to_arg_dict[connection.deviceID]])
                except:
                    print("Exception sending individual message to: " + connection.deviceID)

class MetatoneWebsiteHandler(tornado.web.RequestHandler):
    """
    Handler class for web requests.
    """
    def get(self):
        self.render("index.html")

##############################################

class MetatoneAppConnectionHandler(tornado.websocket.WebSocketHandler):
    """
    Class for handling connection to a Metatone App. Received messages are processed and
    sent to the classifier. Can send OSC formatted messages via the web socket connection.
    """
    deviceID = ''
    app = ''

    def open(self):
        print("Client opened WebSocket")
        # print(str(self.application))
        self.application.connections.add(self)
        logging.info(datetime.now().isoformat() + " Connection Opened.")
        # print("Connections: " + repr(connections))

    def on_message(self, message):
        time = datetime.now()
        process_metatone_message(self, time, message)

    def on_close(self):
        print("!!!! SERVER: Client closed WebSocket: " + self.deviceID)
        remove_metatone_app(self.deviceID)
        logging.info(datetime.now().isoformat() + " Connection Closed, " + self.deviceID)
        self.application.connections.remove(self)
        print("!!!! Removal done.")

    def send_osc(self, address, arguments):
        """
        Attempts to send an OSC formatted message to the client.
        """
        msg = OSC.OSCMessage(address)
        msg.extend(arguments)
        packet = msg.getBinary()
        try:
            self.write_message(packet, binary=True)
        except:
            logging.error("Error sending OSC message to client", exc_info=True)

##############################################
## Top level functions... should get some of these into the Application class.

def process_metatone_message(handler, time, packet):
    """
    Function to decode an OSC formatted string and then process it
    according to its address. Sends processed messages directly
    to the metatoneClassifier module's message handling functions.
    """
    message = OSC.decodeOSC(packet)
    try:
        if "/metatone/touch/ended" in message[0]:
            metatoneClassifier.touch_ended_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/touch" in message[0]:
            # def touch_handler(addr, tags, stuff, source):
            metatoneClassifier.touch_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/switch" in message[0]:
            metatoneClassifier.switch_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/online" in message[0]:
            metatoneClassifier.onlineoffline_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            handler.send_osc("/metatone/classifier/hello", [])
            handler.deviceID = message[2]
            handler.app = message[3]
        elif "/metatone/offline" in message[0]:
            metatoneClassifier.onlineoffline_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/acceleration" in message[0]:
            metatoneClassifier.accel_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/app" in message[0]:
            metatoneClassifier.metatone_app_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        elif "/metatone/targetgesture" in message[0]:
            metatoneClassifier.target_gesture_handler(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
        else:
            print("Got an unknown message! Address was: " + message[0])
            print("Time was: " + str(time))
            print(u'Raw Message Data: {}'.format(packet))
    except():
        print("Message did not decode to a non-empty list.")

def remove_metatone_app(device_id):
    """
    Instructs the Classifier to remove an app with a particular deviceID
    from its list of connected sources.
    """
    print("!!!! Removing App: " + repr(device_id))
    metatoneClassifier.remove_source(device_id)

def clear_metatone_apps():
    """
    Instructs the Classifier to remove ALL connected apps
    from its list of sources.
    """
    print("Clearing all apps from Classifier")
    metatoneClassifier.clear_all_sources()

def bonjour_callback(sdref, flags, error_code, name, regtype, domain):
    """
    Callback function for bonjour service.
    """
    if error_code == pybonjour.kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', regtype)
        print('  domain  =', domain)
        print(str(sdref))
        print(str(flags))

def main():
    """
    Main function loads classifier and sets up bonjour service and web server.
    """
    print("Loading Metatone Classifier.")
    metatoneClassifier.load_classifier()
    metatoneClassifier.start_log()
    print("Metatone Classifier Ready.")
    logging.info("WebServer Logging started - " + metatoneClassifier.logging_filename)
    print ("Classifier WebServer Started - logging to: "
           + metatoneClassifier.logging_filename)

    tornado.options.parse_command_line()
    app = MetatoneWebApplication()
    app.listen(options.port)
    metatoneClassifier.name = options.name
    metatoneClassifier.performance_type = options.type
    logging.info("WebServer Performance type is: " + str(options.type)
                 + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    print("WebServer Performance type is: " + str(options.type)
          + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    metatoneClassifier.performance_composition = random.randint(0, 100)
    metatoneClassifier.WEB_SERVER_MODE = True
    metatoneClassifier.webserver_sendtoall_function = app.send_osc_to_all_clients
    metatoneClassifier.webserver_sendindividual_function = app.send_osc_to_individual_clients

    classification_thread = threading.Thread(target=metatoneClassifier.classify_forever, name="Classification-Thread")

    print("Starting Bonjour Service.")
    bonjour_service_register = pybonjour.DNSServiceRegister(
        name=options.name,
        regtype=METACLASSIFIER_SERVICE_TYPE,
        port=options.port,
        callBack=bonjour_callback)

    try:
        classification_thread.start()
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("\nReceived Ctrl-C - Closing down.")
        metatoneClassifier.stop_classifying()
        clear_metatone_apps()
        bonjour_service_register.close()
        print("Closed down. Bye!")

if __name__ == "__main__":
    main()
