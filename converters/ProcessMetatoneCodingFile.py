import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import argparse


parser = argparse.ArgumentParser(description='Change the date index of a coding file to match the start of the touch log.')
parser.add_argument('filename',help='CSV Gesture Targets File.')

args = parser.parse_args()

input_filename = args.filename


datestring = input_filename
datestring = datestring.replace(".csv","")

datestring = datestring[len(datestring) - 18:]
start_time = datetime.strptime(datestring,"%Y%m%d-%Hh%Mm%Ss")

output_filename = input_filename + '-dateproc.csv'

raw_file = open(input_filename, 'r')
processed_file = open(output_filename,'w')





processed_file.write('time,charles,christina,yvonne,jonathan\n')
message = ""

for line in raw_file:
    line_pieces = line.split(',')
    if (line_pieces[0] != 'time'):
        line_time = line_pieces[0].split(':')
        line_time_delta = timedelta(minutes = float(line_time[0]),seconds = float(line_time[1]))
        # calculate date string
        date_stamp = (start_time + line_time_delta).isoformat()
        processed_file.write(date_stamp +','+ line_pieces[1] +','+ line_pieces[2] +','+ line_pieces[3] +','+ line_pieces[4] + '\n')
    
raw_file.close()
processed_file.close()

print("Converted File for Performance: " + datestring + ", saved to " + output_filename)