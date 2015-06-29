# pylint: disable=line-too-long
"""
Metatone Classifier OSC Server - Runs the classifier using a UDP Socket.
Only useful for local performances and is a bit dodgy in terms of reliability.
"""
from __future__ import print_function
import socket
import logging
import metatone_classifier
import threading
import OSC
import pybonjour
import random

SERVER_NAME = "MetatoneLiveProc"
SERVER_PORT = 9000

PERFORMANCE_TYPE_LOCAL = 0
PERFORMANCE_TYPE_REMOTE = 1
EXPERIMENT_TYPE_BOTH = 2
EXPERIMENT_TYPE_NONE = 3
EXPERIMENT_TYPE_BUTTON = 4
EXPERIMENT_TYPE_SERVER = 5
PERFORMANCE_TYPE_NAMES = [
    "Performance-Local", "Performance-Remote", "Experiment-Both",
    "Experiment-None", "Experiment-Button", "Experiment-Server"]

class MetatoneOSCServer():
    """ 
    An OSC server for Metatone App Performances 
    """

    def __init__(self):
        self.server_thread = None
        self.classification_thread = None
        self.server = None
        self.server_name = SERVER_NAME
        self.server_port = SERVER_PORT
        self.performance_type = PERFORMANCE_TYPE_LOCAL
        self.receive_address = None
        self.find_receive_address()
        print("Loading Metatone Classifier.")
        self.classifier = metatone_classifier.MetatoneClassifier()
        self.classifier.performance_type = self.performance_type
        self.classifier.performance_composition = random.randint(0, 100)
        self.classifier.web_server_mode = False
        self.classifier.start_log()
        logging.info("OSC Server Performance type is: " + str(self.performance_type)
                     + ": " + PERFORMANCE_TYPE_NAMES[self.performance_type])
        print("WebServer Performance type is: " + str(self.performance_type)
              + ": " + PERFORMANCE_TYPE_NAMES[self.performance_type])
        print("Metatone Classifier Ready.")
        self.bonjour_service_register = pybonjour.DNSServiceRegister(
            name=self.server_name,
            regtype="_osclogger._udp.",
            port=self.server_port,
            callBack=bonjour_callback)

    def find_receive_address(self):
        """
        Figures out the local IP address and port that the OSCServer should use and
        starts the Bonjour service.
        """
        searched_ips = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
        #ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])
        # ip = socket.getaddrinfo(socket.gethostname(),9000)[:1][0][4]
        try:
            self.receive_address = (searched_ips[0], self.server_port)
        except IndexError:
            print("Could not find IP address automatically. Using localhost instead.")
            self.receive_address = ("localhost", self.server_port)
        print("Server Address: " + str(self.receive_address))

    def start_osc_server(self):
        """
        Starts the OSCServer serving on a new thread and adds message handlers.
        """
        print("Starting OSC Server and Classification.")
        self.classification_thread = threading.Thread(target=self.classifier.classify_forever, name="Classification-Thread")
        self.classification_thread.start()
        self.server = OSC.OSCServer(self.receive_address)
        self.server.addMsgHandler("/metatone/touch", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/touch/ended", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/switch", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/online", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/offline", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/acceleration", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/app", self.classifier.handle_client_message)
        self.server.addMsgHandler("/metatone/targetgesture", self.classifier.handle_client_message)
        # self.server_thread = threading.Thread(target=self.server.serve_forever, name="OSC-Server-Thread")
        # self.server_thread.start()
        self.server.serve_forever()


    def close_server(self):
        """
        Closes the OSCServer, server thread and Bonjour service reference.
        """
        print("\nClosing OSC Server systems...")
        self.server.close()
        self.bonjour_service_register.close()
        # self.server_thread.join()
        self.classifier.stop_classifying()
        self.classification_thread.join()
        print("Closed.")

def bonjour_callback(service_reference, flags, error_code, name, reg_type, domain):
    """
    Callback function for bonjour service registration.
    """
    if error_code == pybonjour.kDNSServiceErr_NoError:
        print('Registered service:')
        print('  name    =', name)
        print('  regtype =', reg_type)
        print('  domain  =', domain)

def main():
    """
    Main function loads classifier and sets up bonjour service and web server.
    """
    app = MetatoneOSCServer()
    try:
        app.start_osc_server()
    except KeyboardInterrupt:
        print("\nReceived Ctrl-C - Closing down.")
        app.close_server()
        print("Closed down. Bye!")

if __name__ == "__main__":
    main()
