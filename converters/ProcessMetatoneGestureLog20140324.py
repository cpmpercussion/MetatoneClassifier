#import pandas as pd
#import numpy as np
#from datetime import timedelta
#from datetime import datetime
#import argparse


#parser = argparse.ArgumentParser(description='Convert a Metatone OSC Logger file into a useful CSV.')
#parser.add_argument('filename',help='A Metatone Supercollider OSC Log to be converted.')

#args = parser.parse_args()

#input_filename = args.filename

device_names = {
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

input_filename = '/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/2014-03-17T18-30-57-MetatoneOSCLog-gestures.csv'
#input_filename = '/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/2014-03-17T18-09-46-MetatoneOSCLog-gestures.csv'


gesture_filename = input_filename.replace("-gestures.csv","") + '-better_gestures.csv'
raw_file = open(input_filename, 'r')
gesture_file = open(gesture_filename,'w')

gesture_column_names = ['time']
all_gesture_lines = []

for line in raw_file:
    # for device_id in device_names.keys():
    #     if device_id in line:
    #         line = line.replace(device_id,device_names[device_id])

    ## Organise the correct column names.
    if 'time' not in line:
        line = line.replace('\n','')
        parts = line.split(", ")
        gestures = parts[1:]
        line_gestures = {'time':parts[0]}
        for n in range(len(gestures)/2):
            line_gestures[gestures[2*n]] = gestures[2*n + 1]
            if gestures[2*n] not in gesture_column_names:
                gesture_column_names.append(gestures[2*n])

        out_data = [line_gestures[n] for n in gesture_column_names]
        all_gesture_lines.append(out_data)


# write the header.
gesture_file.write(', '.join(gesture_column_names) + '\n')
# write each line.
for row in all_gesture_lines:
    # now write the line
    out_data = ', '.join(row) + '\n'
    gesture_file.write(out_data)

raw_file.close()
gesture_file.close()