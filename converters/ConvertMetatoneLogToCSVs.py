#! /usr/bin/env python
# pylint: disable=line-too-long
"""
This script splits up Metatone Classifier logs into 6 CSV files according to the type of data.
30/06/2014
"""
from __future__ import print_function
import argparse

DEVICE_NAMES = {
    '2678456D-9AE7-4DCC-A561-688A4766C325':'charles', # old
    '97F37307-2A95-4796-BAC9-935BF417AC42':'christina', # old
    '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne', # old
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan', #old
    'D346C530-BBC9-4C1E-9714-F17654BCC3BC':'yvonne', # new names
    '30CB5985-FC54-43FC-8B77-C8BE24AA443C':'charles', # new names
    'E9F60D46-EE37-489A-AD91-4ABC99E2BC80':'jonathan', # new names
    '35F73141-D3D5-4F00-9A28-EC5449A1A73D':'christina', #new names
    '8EEF3773-19CE-4F4D-99BB-2B5BC1CE460C':'christina', # possible christina name from metalonsdale (check this?)
    '16742ED0-5061-4FC8-9BF6-6F23FF76D767':'charles_ipadair',
    '46D2EBCA-A5BD-448A-8DB5-69C39D5220EE':'jonathan_iPad2'
}

# Testing reading file to strings version.
def split_metatone_log_to_dataframes(input):
    """
    Reads a metatone log file into six dataframes.
    unfinished.
    """
    raw_file = open(input, 'r')
    gesture_targets_log = False
    gesture_target_string = 'time,target\n'
    touch_string = 'time,device_id,x_pos,y_pos,velocity\n'
    gesture_string = ""
    transitions_string = 'time,transition_type,spread,ratio\n'
    events_string = 'time,name,event_type\n'
    metatone_messages_string = 'time,type,device_id,label,value\n'
    online_string = 'time,type,device_id,app_id\n'
    gesture_column_names = ['time']
    all_gesture_lines = []
    for line in raw_file:
        for device_id in DEVICE_NAMES.keys():
            if device_id in line:
                line = line.replace(device_id, DEVICE_NAMES[device_id])
        line = line.replace(" ", "")
        if "touch," in line:
            touch_string += line.replace("touch,", "")
        if ("MetatoneLiveProc" in line) or ("MetatoneWebProc" in line):
            events_string += line
        if "metatone," in line:
            metatone_messages_string += line
        if "/metatone/online" in line:
            online_string += line
        if ("stasis" in line) or ("convergence" in line) or ("divergence" in line) or ("development" in line):
            transitions_string += line
        if "/classifier/gestures" in line:
            line = line.replace("/classifier/gestures,", "")
            line = line.replace('\n', '')
            parts = line.split(",")
            gestures = parts[1:]
            line_gestures = {'time':parts[0]}
            for i in range(len(gestures)/2):
                line_gestures[gestures[2*i]] = gestures[2*i + 1]
                if gestures[2*i] not in gesture_column_names:
                    gesture_column_names.append(gestures[2*i])
            out_data = [line_gestures[n] for n in gesture_column_names]
            all_gesture_lines.append(out_data)
        if "/metatone/targetgesture" in line:
            if not gesture_targets_log: 
                print("Found target gestures, opening target gesture file.")
                gesture_targets_log = True
            line = line.replace("/metatone/targetgesture,", "")
            gesture_target_string += line
    # now process these files at dataframes.
       



def process_metatone_file_to_csv(input_filename):
    """
    Old process for processing metatone log.
    Outputs six CSV files.
    """
    # only open the gesture_target_file if there are gesture target messages present.
    found_target_gestures = False
    touch_filename = input_filename.replace(".log", "") + '-touches.csv'
    gesture_filename = input_filename.replace(".log", "") + '-gestures.csv'
    transitions_filename = input_filename.replace(".log", "") + '-transitions.csv'
    events_filename = input_filename.replace(".log", "") + '-events.csv'
    metatone_filename = input_filename.replace(".log", "") + '-metatone.csv'
    online_filename = input_filename.replace(".log", "") + '-online.csv'
    gesture_target_filename = input_filename.replace(".log", "") + '-gesturetargets.csv'

    raw_file = open(input_filename, 'r')
    touch_file = open(touch_filename, 'w')
    gesture_file = open(gesture_filename, 'w')
    transitions_file = open(transitions_filename, 'w')
    events_file = open(events_filename, 'w')
    metatone_file = open(metatone_filename, 'w')
    online_file = open(online_filename, 'w')

    touch_file.write('time,device_id,x_pos,y_pos,velocity\n')
    transitions_file.write('time,transition_type,spread,ratio\n')
    events_file.write('time,name,event_type\n')
    metatone_file.write('time,type,device_id,label,value\n')
    online_file.write('time,type,device_id,app_id\n')

    gesture_column_names = ['time']
    all_gesture_lines = []

    for line in raw_file:
        for device_id in DEVICE_NAMES.keys():
            if device_id in line:
                line = line.replace(device_id, DEVICE_NAMES[device_id])
        line = line.replace(" ", "")
        if "touch," in line:
            #touch_file.write(line.replace("touch, ",""))
            touch_file.write(line.replace("touch,", ""))
        if ("MetatoneLiveProc" in line) or ("MetatoneWebProc" in line):
            events_file.write(line)
        if "metatone," in line:
            metatone_file.write(line)
        if "/metatone/online" in line:
            online_file.write(line)
        if ("stasis" in line) or ("convergence" in line) or ("divergence" in line) or ("development" in line):
            transitions_file.write(line)

        if "/classifier/gestures" in line:
            #line = line.replace("/classifier/gestures, ","")
            line = line.replace("/classifier/gestures,", "")
            line = line.replace('\n', '')
            parts = line.split(",")
            gestures = parts[1:]
            line_gestures = {'time':parts[0]}
            for n in range(len(gestures)/2):
                line_gestures[gestures[2*n]] = gestures[2*n + 1]
                if gestures[2*n] not in gesture_column_names:
                    gesture_column_names.append(gestures[2*n])
            out_data = [line_gestures[n] for n in gesture_column_names]
            all_gesture_lines.append(out_data)

        if "/metatone/targetgesture" in line:
            if not found_target_gestures: 
                print("Found target gestures, opening target gesture file.")
                gesture_target_file = open(gesture_target_filename, 'w')
                gesture_target_file.write('time,target\n')
                found_target_gestures = True
            # open_gesture_target_file()
            line = line.replace("/metatone/targetgesture,", "")
            gesture_target_file.write(line)

    # write the gesture file:
    # write the header.
    gesture_file.write(','.join(gesture_column_names) + '\n')
    # write each line.
    for row in all_gesture_lines:
        # now write the line
        out_data = ','.join(row) + '\n'
        gesture_file.write(out_data)

    raw_file.close()
    touch_file.close()
    gesture_file.close()
    transitions_file.close()
    events_file.close()
    metatone_file.close()
    online_file.close()

def main():
    """
    Main function - parses the filename from the command line
    and processes the log file to six CSVs.
    """
    parser = argparse.ArgumentParser(description='Convert a Metatone Classifier log file into a set of useful CSV.')
    parser.add_argument('filename', help='A Metatone Classifier .log file to be converted.')
    args = PARSER.parse_args()
    input_filename = args.filename
    #input_filename = '/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/2014-03-17T18-30-57-MetatoneOSCLog.txt'
    process_metatone_file_to_csv(input_filename)

if __name__ == '__main__':
    main()
