#!/usr/bin/python
# pylint: disable=line-too-long
"""
metatone_classifier Module

Copyright 2015 Charles Martin

http://metatone.net
http://charlesmartin.com.au

This file can be executed by itself (python metatone_classifier.py) or used as a module
by another python process.

This file contains the MetatoneClassifier class which defines what MetatoneClassifier does at each run-step
during a performance. The classification features and training is done in the generate_classifier module.

If using as a module, call the main() function to initiate the normal run loop.

TODO:
- system for holding messages that should be sent to each iPad that connects?
- better system for naming devices.
"""
from __future__ import print_function
import OSC
import time
import socket
from datetime import timedelta
from datetime import datetime
import pandas as pd
import logging
import transitions
import generate_classifier
import os
import random
import touch_performance_player  # handles sound object playback for generative ensemble cases
import tensorflow as tf
import gesture_rnn  # LSTM RNN for gesture calculation.

##
SERVER_NAME = "MetatoneLiveProc"
SERVER_PORT = 9000
CLOUD_SERVER_IP = "107.170.207.234"
##
METATONE_RECEIVING_PORT = 51200
##
PERFORMANCE_TYPE_LOCAL = 0
PERFORMANCE_TYPE_REMOTE = 1
EXPERIMENT_TYPE_BOTH = 2
EXPERIMENT_TYPE_NONE = 3
EXPERIMENT_TYPE_BUTTON = 4
EXPERIMENT_TYPE_SERVER = 5
##
PERFORMANCE_TYPE = 4  # this can be 0-5
PERFORMANCE_COMPOSITION = 4  # this can be any random int.
PERFORMANCE_EVENT_NAME = "MetatonePerformanceStart"
VISUALISER_MODE_ON = True
VISUALISER_PORT = 61200
VISUALISER_HOST = 'localhost'
MAX_GESTURE_LENGTH = 300  # Corresponds to five minutes of performance time.
DEVICE_NAMES = {
    # '2678456D-9AE7-4DCC-A561-688A4766C325':'charles', # old
    # '95585C5C-C1C1-4612-9836-BFC68B0DC36F':'charles',
    # '97F37307-2A95-4796-BAC9-935BF417AC42':'christina', # old
    # '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne', # old
    # '2C4C4043-B7F7-4C22-B930-1472B1E18DBF':'yvonne',
    # '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan', #old
    # 'D346C530-BBC9-4C1E-9714-F17654BCC3BC':'yvonne', # new names
    # '30CB5985-FC54-43FC-8B77-C8BE24AA443C':'charles', # new names
    # 'E9F60D46-EE37-489A-AD91-4ABC99E2BC80':'jonathan', # new names
    # '00088B8E-D27C-4AE1-8102-5FE318589D3E':'jonathan',
    # '35F73141-D3D5-4F00-9A28-EC5449A1A73D':'christina', #new names
    # '8EEF3773-19CE-4F4D-99BB-2B5BC1CE460C':'christina', #14.07.10
    # '74C29BE8-6B34-4032-8E74-FCEC42DF3D5B':'christina',
    # '16742ED0-5061-4FC8-9BF6-6F23FF76D767':'charles_ipadair',
    # '0E98DD2F-94C2-45EE-BEC5-18718CA36D8B':'charles_ipadair',
    # '6EAD764A-E424-48EB-9672-03EF44679A5E':'iPad2-64-white',
    # '670EC230-5C3E-4759-B70F-5FDBCE14189B':'charles-iphone5'
}
# Column names for feature vectors.
FEATURE_VECTOR_COLUMNS = ['centroid_x', 'centroid_y', 'std_x',
                          'std_y', 'freq', 'movement_freq', 'touchdown_freq', 'velocity']
GESTURE_CLASS_NAMES = ['n', 'ft', 'st', 'fs', 'fsa', 'vss', 'bs',
                       'ss', 'c']

# # # # #
# Utility Functions
# # # # #


def ensure_dir(file_name):
    """
    Checks if a directory exists in the local directory,
    if it doesn't, creates it.
    """
    dir_to_make = os.path.dirname(file_name)
    if not os.path.exists(dir_to_make):
        os.makedirs(dir_to_make)


def dummy_websocket_sender(address, arguments):
    """
    Dummy function: when running in webserver mode, the server replaces this with functions
    to send data to correct clients.
    """
    return
    # do nothing


def get_device_name(device_id):
    """
    Returns the device's name if known.
    This functionality needs work! Names shouldn't be hardcoded.
    """
    if device_id in DEVICE_NAMES:
        return DEVICE_NAMES[device_id]
    else:
        return device_id


def pretty_print_classes(classes):
    """
    Returns a string of each active device matched to a human
    readable gesture state.
    """
    names = list(classes)
    pretty_classes = {}
    result = ""
    for name in names:
        pretty_classes[name] = GESTURE_CLASS_NAMES[classes[name]]
        result += name + " : " + GESTURE_CLASS_NAMES[classes[name]] + "\n"
    # return pretty_classes
    return result


def pretty_print_state(state):
    """
    Returns a string of each part of the performance state
    labelled with its meaning.
    """
    result = "Transition Type: " + state[0] + "\n"
    result += "Spread: " + str(state[1]) + "\n"
    result += "Ratio: " + str(state[2])
    return result


def print_performance_state(state_tuple):
    """
    Given the performance state tuple returned by classify_performance(),
    this function prints it out nicely on the screen.
    """
    print("# # # # # # # # # # # #")
    print("Classification: " + str(datetime.now()))
    classes = state_tuple[0]
    if classes:
        print(pretty_print_classes(classes))
    # state = state_tuple[1]
    # if state:
    #     print(pretty_print_state(state))
    # Print Flux Increase:
    flux_series = state_tuple[3]
    if isinstance(flux_series, pd.Series):  # check if it is a time series
        flux_series = flux_series.dropna()
        if flux_series.count() > 0:
            flux_latest = flux_series.tolist()[-1]
            print("Latest flux reading: " + str(round(flux_latest, 3)))
        if flux_series.count() > 1:
            flux_diff = flux_series[-2:].diff().dropna().tolist()[0]
            print("Flux difference was: " + str(round(flux_diff, 3)))
    newidea = state_tuple[2]
    if newidea:
        print("!! New Idea Detected !!")
    print("# # # # # # # # # # # #")

###########################
#
# Classifier Class
#
###########################


class MetatoneClassifier:
    """ A classifier that mediates Metatone touch-screen performances.
    """

    def __init__(self, lead_player_device_id=""):
        """ Initialise the MetatoneClassifier """
        self.lead_player_device_id = lead_player_device_id
        if self.lead_player_device_id is not "":
            print("Following lead player:", self.lead_player_device_id)
        self.classifying_forever = False
        self.web_server_mode = False
        self.sources_to_remove = []
        self.classifier = generate_classifier.load_classifier()
        self.osc_sources = {}
        self.active_names = []
        self.active_apps = {}
        self.osc_client = OSC.OSCClient()
        self.touch_messages = []
        self.classified_gestures = []
        self.webserver_sendtoall_function = dummy_websocket_sender
        self.webserver_sendindividual_function = dummy_websocket_sender
        self.update_gestures_function = dummy_websocket_sender
        self.name = SERVER_NAME
        self.performance_type = PERFORMANCE_TYPE_LOCAL
        self.performance_composition = random.randint(0, 100)
        self.visualiser_mode = VISUALISER_MODE_ON
        self.logging_filename = ""

    def classify_touch_messages(self, messages):
        """
        Given a list of touch messages, generates a gesture class for each
        active device for the preceding 5 seconds. Returned as a
        dictionary.
        """
        if not messages:
            return self.classify_empty_touch_messages()
        # This line can fail with a ValueError exception
        touch_frame = pd.DataFrame(messages, columns=['time',
                                                      'device_id', 'x_pos', 'y_pos', 'velocity'])
        touch_frame = touch_frame.set_index('time')
        delta = timedelta(seconds=-5)
        time_now = datetime.now()
        touch_frame = touch_frame.between_time((time_now + delta).time(), time_now.time())
        classes = {}
        for name in self.active_names:
            features = generate_classifier.feature_frame(touch_frame.ix[touch_frame['device_id'] == name])
            gesture = self.classifier.predict(features[FEATURE_VECTOR_COLUMNS][-1:])
            classes[name] = list(gesture)[0]
        return classes

    def classify_empty_touch_messages(self):
        """
        Returns a valid classes dict with 0 in each value.
        Useful when there are no messages but active devices.
        """
        classes = {}
        for name in self.active_names:
            classes[name] = 0
        return classes

    def make_gesture_frame(self, gesture_log):
        """
        Takes a log of gestures and returns a time series
        with columns for each active device.
        """
        if not gesture_log:
            return pd.DataFrame(columns=['time'])
        gesture_columns = ['time']
        gesture_columns.extend(self.active_names)
        gesture_frame = pd.DataFrame(gesture_log, columns=gesture_columns).set_index('time')
        return gesture_frame

    ######################################
    #
    # Logging data functions
    #
    ######################################

    def start_log(self):
        """
        Start a new log with the filename set to the current time.
        Checks that we have a log directory and creates it if necessary.
        """
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.logging_filename = datetime.now().isoformat().replace(":", "-")[:19] + "-MetatoneOSCLog.log"
        logging.basicConfig(filename="logs/" + self.logging_filename, level=logging.DEBUG, format='%(message)s')
        logging.info("Logging started - " + self.logging_filename)
        print("Classifier Server Started - logging to: " + self.logging_filename)

    def log_messages(self, message):
        """
        Log the message line to system log.
        """
        logging.info(str(message).replace("[", "").replace("]", "").replace("'", ""))

    def record_latest_gestures(self, classes):
        """
        Given a dict of classes, adds them to the system log
        as well as the global list of gestures used for performance
        tracking.
        Also ensures that the global gesture list does not exceed 10 minutes of gestures.
        """
        if not classes:
            return
        current_time = datetime.now()
        # First add to the file log.
        message_log_line = [current_time.isoformat()]
        message_log_line.append("/classifier/gestures")
        for key in classes.keys():
            message_log_line.append(key)
            message_log_line.append(classes[key])
        self.log_messages(message_log_line)
        # Now add to the gesture log.
        # TODO: add the whole classes dict! Not just the list of gestures! how stupid!
        classes = [classes[n] for n in classes.keys()]
        classes.insert(0, current_time)
        self.classified_gestures.append(classes)

    def trim_touch_messages(self):
        """
        Trims the global touch_messages list to the last five seconds of activity.
        """
        current_time = datetime.now()
        delta = timedelta(seconds=-5)
        self.touch_messages = [x for x in self.touch_messages if x[0] > current_time + delta]

    def trim_gesture_log(self):
        """
        Trims the global gesture list to the length defined in MAX_GESTURE_LENGTH.
        This runs after every classification step.
        """
        if len(self.classified_gestures) > MAX_GESTURE_LENGTH:
            self.classified_gestures = self.classified_gestures[-MAX_GESTURE_LENGTH:]

    ######################################
    #
    # OSC sending Functions.
    #
    ######################################

    def send_gestures(self, classes):
        """
        Send gesture classes to the relevant active devices.
        """
        for name in self.osc_sources.keys():
            if name in classes.keys():
                msg = OSC.OSCMessage("/metatone/classifier/gesture")
                msg.extend([name, GESTURE_CLASS_NAMES[classes[name]]])
                try:
                    self.osc_client.sendto(msg, self.osc_sources[name], timeout=10.0)
                except OSC.OSCClientError as err:
                    print("Couldn't send gestures to " + name + ". OSCClientError")
                    print(msg)
                    print(err)
                except socket.error:
                    print("Couldn't send gestures to " + name + ", bad address (removed).")
                    self.remove_source(name)
        if self.web_server_mode:
            class_strings = {}
            for name in classes.keys():
                class_strings[name] = GESTURE_CLASS_NAMES[classes[name]]
            self.webserver_sendindividual_function("/metatone/classifier/gesture", class_strings)

    def send_message_to_sources(self, msg):
        """
        Sends a message to all active devices.
        """
        for name in self.osc_sources.keys():
            try:
                self.osc_client.sendto(msg, self.osc_sources[name], timeout=10.0)
            except OSC.OSCClientError as err:
                print("Couldn't send message to " + name + ". OSCClientError")
                print(msg)
                print(err)
            except socket.error:
                print("Couldn't send message to " + name + ", bad address (removed).")
                self.remove_source(name)
        if self.web_server_mode:
            self.webserver_sendtoall_function(msg.address, msg.values())
        log_line = [datetime.now().isoformat()]
        log_line.extend(msg)
        self.log_messages(log_line)

    def send_performance_start_message(self, device_name):
        """
        Function to send an individual performance start message to a source.
        Should run when a source first connects.
        """
        msg = OSC.OSCMessage("/metatone/performance/start")
        msg.append(PERFORMANCE_EVENT_NAME)
        msg.append(device_name)
        msg.append(self.performance_type)
        msg.append(self.performance_composition)
        try:
            self.osc_client.sendto(msg, self.osc_sources[device_name], timeout=10.0)
        except OSC.OSCClientError as err:
            print("Couldn't send performance start to " + device_name + ". OSCClientError")
            print(msg)
            print(err)
        except socket.error:
            print("Couldn't send performance start to " + device_name + ", bad address (removed).")
            self.remove_source(self.osc_sources[device_name])
        if self.web_server_mode:
            self.webserver_sendtoall_function(msg.address, msg.values())

    def send_performance_end_message(self, device_name):
        """
        Function to send an indivudal performance end message to source.
        """
        msg = OSC.OSCMessage("/metatone/performance/end")
        msg.append(PERFORMANCE_EVENT_NAME)
        msg.append(device_name)
        try:
            self.osc_client.sendto(msg, self.osc_sources[device_name], timeout=10.0)
        except OSC.OSCClientError as err:
            print("Couldn't send performance end to " + device_name + ". OSCClientError")
            print(msg)
            print(err)
        except socket.error:
            print("Couldn't send performance end to " + device_name + ", bad address (removed).")
            self.remove_source(self.osc_sources[device_name])
        if self.web_server_mode:
            self.webserver_sendtoall_function(msg.address, msg.values())

    def send_touch_to_visualiser(self, touch_data):
        """
        Sends touch data to the standard visualiser address.
        """
        msg = OSC.OSCMessage("/metatone/touch")
        msg.extend(touch_data)
        try:
            self.osc_client.sendto(msg, (VISUALISER_HOST, VISUALISER_PORT))
        except:
            msg = ""

    ######################################
    #
    # Functions for keeping track of Metatone Clients.
    #
    ######################################

    def add_source_to_list(self, name, source):
        """
        Called whenever an OSC messaged is received.
        If a source is not listed, it's added to the dictionary,
        otherwise - nothing happens.
        """
        source_address = (source[0], METATONE_RECEIVING_PORT)
        if name not in self.osc_sources.keys():
            self.osc_sources[name] = source_address
            # TODO send new performance start message.

    def add_active_app(self, name, app):
        """
        Adds the current app whenever an online message is received.
        """
        self.active_apps[name] = app

    def remove_source(self, name):
        """
        Queues a touch-data source for removal from processing.
        Called after a source closes it's connection.
        The sources are removed by process_source_removal() which only
        runs inside the classification thread.
        """
        self.sources_to_remove.append(name)

    def process_source_removal(self):
        """ Removes the touch data sources in the global list.
        Should only be run inside the classification thread.
        """
        for name in self.sources_to_remove:
            print("CLASSIFIER: Removing a source: " + name)
            print("Sources: " + repr(self.osc_sources))
            print("Active Names: " + repr(self.active_names))
            if name in self.osc_sources:
                del self.osc_sources[name]
            if name in self.active_names:
                self.active_names.remove(name)  # can't do this until I fix gesture logging... needs to be dictionary not list.
        self.sources_to_remove = []

    def clear_all_sources(self):
        """
        Sends a performance end message to all connected apps and then removes them all.
        """
        for name in self.osc_sources.keys():
            self.send_performance_end_message(name)  # send performance end messages.
        self.osc_sources = {}
        self.active_names = []
        self.active_apps = []

    def add_active_device(self, device_id):
        """
        Adds a device_name to the list if it isn't already on it.
        """
        device_name = get_device_name(device_id)
        if device_name not in self.active_names:
            self.active_names.append(device_name)

    ######################################
    #
    # Classification Loop Functions
    #
    ######################################

    def generate_neural_gestures(self, classes):
        """ Code for generating ensemble gesture classes when running as neural ensemble.
        """
        if self.lead_player_device_id in classes.keys():
            lead_gesture = int(classes[self.lead_player_device_id])
            # Retrieve ensemble gestures
            print("Generating Ensemble Gestures in response to:", lead_gesture)
            try:
                self.ensemble_gestures = self.network.generate_gestures(lead_gesture, self.ensemble_gestures, self.tf_session)
                print("RNN Ensemble:", self.ensemble_gestures)
            except Exception as e:
                print("Couldn't generate ensemble gestures:", e)
            touch_performance_player.update_gestures(self.ensemble_gestures)
            ensemble = list(self.active_names)  # make copy while editing.
            ensemble.remove(self.lead_player_device_id)
            ensemble_size = min(len(self.ensemble_gestures), len(ensemble))
            for i in range(ensemble_size):
                classes[ensemble[i]] = self.ensemble_gestures[i]
        return classes

    def classify_performance(self):
        """
        Classifies the current performance state.
        Sends messages regarding current gestures, new ideas and other state.
        Designed to be used in a loop.
        """
        try:
            classes = self.classify_touch_messages(self.touch_messages)
        except:
            print("METATONE_CLASSIFIER: Error Classifying Messages.")
            classes = False
        try:
            if classes:
                classes = self.generate_neural_gestures(classes)  # includes RNN gesture generation.
                self.send_gestures(classes)
                self.record_latest_gestures(classes)
            gestures = self.make_gesture_frame(self.classified_gestures).fillna(0)
        except:
            print("METATONE_CLASSIFIER: Error Making Gesture Frame.")
            raise
        try:
            latest_gestures = transitions.trim_gesture_frame(gestures)
            transition_matrices = transitions.calculate_group_transitions_for_window(latest_gestures, '15s')
            flux_series = transitions.calculate_flux_series(transition_matrices)
            if isinstance(transition_matrices, pd.Series):  # .index.is_all_dates:  # check that transition_matrices is a time series
                state = transitions.transition_state_measure(transition_matrices[-1])
            else:
                state = False
        except:
            print("METATONE_CLASSIFIER: Couldn't perform transition calculations.")
            state = False
            raise  # TODO - figure out why this fails sometimes.

        if state:
            msg = OSC.OSCMessage("/metatone/classifier/ensemble/state")
            msg.extend([state[0], state[1], state[2]])
            self.send_message_to_sources(msg)
        newidea = transitions.is_new_idea(flux_series)
        if newidea:
            msg = OSC.OSCMessage("/metatone/classifier/ensemble/event/new_idea")
            msg.extend([SERVER_NAME, "new_idea"])
            self.send_message_to_sources(msg)
        return (classes, state, newidea, flux_series)

    def classify_forever(self):
        """
        Starts a classification process that repeats every second.
        This blocks the thread.
        """
        # Vars for LSTM Evaluation
        self.network = gesture_rnn.GestureRNN(mode="run")
        self.tf_session = tf.Session()
        self.network.prepare_model_for_running(self.tf_session)
        self.ensemble_gestures = [0, 0, 0]
        # Classify forever code.
        self.classifying_forever = True
        while self.classifying_forever:
            try:
                start_time = datetime.now()
                current_state = self.classify_performance()
                print_performance_state(current_state)
                if current_state[0] is not False:  # used in error condition
                    self.update_gestures_function(current_state[0].values())  # Update with classified gestures.
                self.trim_touch_messages()
                self.trim_gesture_log()
                # self.process_source_removal()
                end_time = datetime.now()
                delta_seconds = (end_time - start_time).total_seconds()  # process as timedelta
                print("(Classification took: " + str(delta_seconds) + "s)")
                print("Length of global gesture list: " + str(len(self.classified_gestures)) + "\n")
                time.sleep(max(0, 1 - delta_seconds))
            except:
                print("### Couldn't perform analysis - exception. ###")
                raise

    def stop_classifying(self):
        """
        Stops the classification process and also shuts down the server.
        """
        self.classifying_forever = False
        time.sleep(2)
        touch_performance_player.stop_performance()
        self.clear_all_sources()

    def start_remote_performer(self, name, address):
        """ Starts a remote performer as a touch_performance_player """
        print("Starting remote performer:", name, ",", address)
        touch_performance_player.add_new_performer(name, address)

    def handle_client_message(self, address, tags, contents, source):
        """
        Handles messages from Metatone clients.
        """
        self.add_source_to_list(get_device_name(contents[0]), source)
        self.add_active_device(contents[0])
        current_time = datetime.now()
        try:
            if ("/metatone/touch" in address) and (tags == "sfff"):
                message = [current_time.isoformat(), "touch",
                           get_device_name(contents[0]), contents[1],
                           contents[2], contents[3]]
                self.touch_messages.append([current_time,
                                            get_device_name(contents[0]), contents[1],
                                            contents[2], contents[3]])
                if self.visualiser_mode:
                    self.send_touch_to_visualiser(contents)
            elif ("/metatone/touch/ended" in address) and (tags == "s"):
                message = [current_time.isoformat(), "touch/ended", get_device_name(contents[0])]
            elif ("/metatone/switch" in address) and (tags == "sss"):
                message = [current_time.isoformat(), "switch",
                           get_device_name(contents[0]), contents[1],
                           contents[2]]
            elif ("/metatone/online" in address) and (tags == "ss"):
                self.send_performance_start_message(get_device_name(contents[0]))
                message = [current_time.isoformat(), address, get_device_name(contents[0]), contents[1]]
                print(get_device_name(contents[0]) + " is online with " + contents[1] + ".")
                self.add_active_app(get_device_name(contents[0]), contents[1])
            elif ("/metatone/offline" in address) and (tags == "ss"):
                message = [current_time.isoformat(), address, get_device_name(contents[0]), contents[1]]
                print(get_device_name(contents[0]) + " is offline with " + contents[1] + ".")
            elif ("/metatone/acceleration" in address) and (tags == "sfff"):
                # Just logs message - no action.
                message = [current_time.isoformat(), "accel",
                           get_device_name(contents[0]), contents[1],
                           contents[2], contents[3]]
            elif ("/metatone/app" in address) and (tags == "sss"):
                message = [current_time.isoformat(), "metatone",
                           get_device_name(contents[0]), contents[1],
                           contents[2]]
                if self.web_server_mode:  # Repeat message back to Metatone Devices.
                    self.webserver_sendtoall_function(address, contents)
            elif "/metatone/targetgesture" in address:
                message = [current_time.isoformat(), address, contents[0]]
                # print("Capturing Target Gesture: " + str(contents[0]))
            else:
                print("Got an unknown message! Address was: " + address)
                print("Time was: " + str(current_time.isoformat()))
                message = [current_time.isoformat(), "/classifier/error", "unknown message"]
            self.log_messages(message)
        except():
            print("Message did not decode to a non-empty list.")
