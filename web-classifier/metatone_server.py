# pylint: disable=line-too-long
"""
Metatone Classifier Server - Runs the classifier using a web socket.
Appropriate for local or remote server use.
"""
from __future__ import print_function
import logging
import metatone_classifier
import threading
import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import define, options
from tornado.concurrent import Future
from tornado import gen
import tornado.web
import tornado.websocket
import os.path
import OSC
import pybonjour
from datetime import datetime
import random
import matplotlib.pyplot as plt, mpld3
import numpy as np


define("port", default=8888, help="run on the given port", type=int)
define("name", default='MetatoneWebProc', help="name for webserver application", type=str)
define("type", default=0, help="Type of performance to start. 0 = Local, 1 = Remote, 2 = Both, 3 = None, 4 = Button, 5 = Server, 6 = ButtonFade", type=int)
define("matplotlib")  # so it will work with emacs iPython
define("colors")  # so it will work with emacs iPython
##
PERFORMANCE_TYPE_LOCAL = 0
PERFORMANCE_TYPE_REMOTE = 1
EXPERIMENT_TYPE_BOTH = 2
EXPERIMENT_TYPE_NONE = 3
EXPERIMENT_TYPE_BUTTON = 4
EXPERIMENT_TYPE_SERVER = 5
EXPERIMENT_TYPE_BUTTON_FADE = 6
PERFORMANCE_TYPE_NAMES = ["Performance-Local", "Performance-Remote",
                          "Experiment-Both", "Experiment-None", "Experiment-Button",
                          "Experiment-Server", "Experiment-ButtonFade"]
METACLASSIFIER_SERVICE_TYPE = "_metatoneclassifier._tcp."
FAKE_OSC_IP_ADDRESS = '127.0.0.1'
FAKE_OSC_PORT = 9999
FAKE_OSC_SOURCE = (FAKE_OSC_IP_ADDRESS, FAKE_OSC_PORT)


class PerformanceBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 1200

    def wait_for_gestures(self, cursor=None):
        # Construct a Future to return to our caller.  This allows
        # wait_for_messages to be yielded from a coroutine even though
        # it is not a coroutine itself.  We will set the result of the
        # Future when results are available.
        result_future = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.cache[-new_count:])
                return result_future
        self.waiters.add(result_future)
        return result_future

    def cancel_wait(self, future):
        self.waiters.remove(future)
        # Set an empty result to unblock any coroutines waiting.
        future.set_result([])

    def new_gestures(self, gestures):
        logging.info("Updating new gestures to %r listeners", len(self.waiters))
        for future in self.waiters:
            future.set_result(gestures)
        self.waiters = set()
        self.cache.extend(gestures)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


global_performance_buffer = PerformanceBuffer()

test_gestures = [[0,1,2,3],[4,5,6,7],[8,0,1,2]]


class GesturesUpdatesHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        cursor = self.get_argument("cursor", None)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = global_performance_buffer.wait_for_gestures(cursor=cursor)
        gestures = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(gestures=gestures))

    def on_connection_close(self):
        global_performance_buffer.cancel_wait(self.future)


class MetatoneWebApplication(tornado.web.Application):
    """
    Main Web Application Class.
    """
    def __init__(self, classifier_object):
        self.classifier = classifier_object
        self.connections = set()
        self.clients = dict()
        handlers = [
            (r"/", MetatoneWebsiteHandler),
            (r"/classifier", MetatoneAppConnectionHandler),
            (r"/a/message/updates", GesturesUpdatesHandler),
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

    def process_metatone_message(self, handler, time, packet):
        """
        Function to decode an OSC formatted string and then process it
        according to its address. Sends processed messages directly
        to the metatone_classifier module's message handling functions.
        """
        message = OSC.decodeOSC(packet)
        try:
            if "/metatone/touch/ended" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/touch" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/switch" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/online" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
                handler.send_osc("/metatone/classifier/hello", [])
                handler.deviceID = message[2]
                handler.app = message[3]
            elif "/metatone/offline" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/acceleration" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/app" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            elif "/metatone/targetgesture" in message[0]:
                self.classifier.handle_client_message(message[0], message[1][1:], message[2:], FAKE_OSC_SOURCE)
            else:
                print("Got an unknown message! Address was: " + message[0])
                print("Time was: " + str(time))
                print(u'Raw Message Data: {}'.format(packet))
        except():
            print("Message did not decode to a non-empty list.")

    def update_performance_gestures(self, gestures):
        """
        Updates the performance buffer with a new list of gestures (e.g., [2, 3, 0, 1])
        """
        global_performance_buffer.new_gestures(gestures)

    def remove_metatone_app(self, device_id):
        """
        Instructs the Classifier to remove an app with a particular deviceID
        from its list of connected sources.
        """
        print("!!!! Removing App: " + repr(device_id))
        self.classifier.remove_source(device_id)

    def clear_metatone_apps(self):
        """
        Instructs the Classifier to remove ALL connected apps
        from its list of sources.
        """
        print("Clearing all apps from Classifier")
        self.classifier.clear_all_sources()


class MetatoneWebsiteHandler(tornado.web.RequestHandler):
    """
    Handler class for web requests.
    """
    def get(self):
        self.render("index.html", gestures=test_gestures, plot=generate_gesture_plot(test_gestures))  # gestures = global_performance_buffer.cache



class MetatoneAppConnectionHandler(tornado.websocket.WebSocketHandler):
    """
    Class for handling connection to a Metatone App. Received messages are processed and
    sent to the classifier. Can send OSC formatted messages via the web socket connection.
    """
    deviceID = ''
    app = ''

    def check_origin(self, origin):
        return True

    def open(self):
        print("Client opened WebSocket")
        # print(str(self.application))
        self.application.connections.add(self)
        logging.info(datetime.now().isoformat() + " Connection Opened.")
        # print("Connections: " + repr(connections))

    def on_message(self, message):
        time = datetime.now()
        self.application.process_metatone_message(self, time, message)

    def on_close(self):
        print("!!!! SERVER: Client closed WebSocket: " + self.deviceID)
        self.application.remove_metatone_app(self.deviceID)
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
# Top level functions... should get some of these into the Application class.


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


def generate_gesture_plot(gestures):
    """
    Generates an HTML plot of the current gestures.
    """
    fig, ax = plt.subplots()
    plt.yticks(np.arange(9), ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs', 'ss', 'c'])
    plt.xticks(np.arange(len(gestures)))
    plt.plot(gestures, marker='o', markersize=20, lw=5, alpha=0.7)
    return mpld3.fig_to_html(fig)


def main():
    """
    Main function loads classifier and sets up bonjour service and web server.
    """
    print("Loading Metatone Classifier.")
    classifier = metatone_classifier.MetatoneClassifier()
    classifier.start_log()
    print("Metatone Classifier Ready.")
    logging.info("WebServer Logging started - " + classifier.logging_filename)
    print("Classifier WebServer Started - logging to: " + classifier.logging_filename)

    tornado.options.parse_command_line()
    app = MetatoneWebApplication(classifier)
    app.listen(options.port)
    classifier.name = options.name
    classifier.performance_type = options.type
    logging.info("WebServer Performance type is: " + str(options.type) + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    print("WebServer Performance type is: " + str(options.type) + ": " + PERFORMANCE_TYPE_NAMES[options.type])
    classifier.performance_composition = random.randint(0, 100)
    classifier.web_server_mode = True
    classifier.webserver_sendtoall_function = app.send_osc_to_all_clients
    classifier.webserver_sendindividual_function = app.send_osc_to_individual_clients
    classification_thread = threading.Thread(target=classifier.classify_forever, name="Classification-Thread")
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
        classifier.stop_classifying()
        app.clear_metatone_apps()
        bonjour_service_register.close()
        print("Closed down. Bye!")


if __name__ == "__main__":
    main()
