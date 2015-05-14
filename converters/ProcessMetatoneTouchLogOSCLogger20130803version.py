"""
Convert a Metatone OSC Logger file into a useful CSV.
Superceded.
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='Convert a Metatone OSC Logger file into a useful CSV.')
parser.add_argument('filename',help='A Metatone Supercollider OSC Log to be converted.')
args = parser.parse_args()
input_filename = args.filename
#input_filename = '/Users/charles/Dropbox/Metatone/20130420/MetatoneOSCLog-20130420-14h55'
#input_filename = '/Users/charles/Dropbox/Metatone/20130421/MetatoneOSCLog-20130421-11h38'
#input_filename = '/Users/charles/Dropbox/Metatone/20130427/MetatoneOSCLog-20130427-17h29.txt'
#input_filename = '/Users/charles/Dropbox/Metatone/20130504/MetatoneOSCLog-20130504-12h12'
#input_filename = '/Users/charles/Dropbox/Metatone/20130504/MetatoneOSCLog-20130504-14h23'
#datestring = input_filename.replace("/Users/charles/Dropbox/Metatone/","");
datestring = input_filename
datestring = datestring.replace(".txt","")
#datestring = datestring[24:]
datestring = datestring[len(datestring) - 18:]
start_time = datetime.strptime(datestring,"%Y%m%d-%Hh%Mm%Ss")
output_filename = input_filename + '-touches.csv'
raw_file = open(input_filename, 'r')
processed_file = open(output_filename,'w')
#first_time = 14.837146462
device_names = {
    '2678456D-9AE7-4DCC-A561-688A4766C325':'charles',
    '97F37307-2A95-4796-BAC9-935BF417AC42':'christina',
    '6769FE40-5F64-455B-82D4-814E26986A99':'yvonne',
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'jonathan'}
processed_file.write('time,device_id,x_pos,y_pos,velocity\n')

message = ""
for line in raw_file:
    line = line.replace("\n","");
    line = line.replace("< (","");
    line = line.replace(") (","");
    line = line.replace(")>","");
    line = line.replace("\"","");
    line = line.replace("    "," ");
    line = line.replace(",","");
    line_pieces = line.split()
    if (line_pieces[2] == "/metatone/touch"):
        # calculate date string
        date_stamp = (start_time + 
            timedelta(seconds = float(line_pieces[0]))).isoformat()
        # alternatively...
        # date_stamp = line_piece[0]
        # write the line...
        processed_file.write(date_stamp +','+ device_names[line_pieces[3]] +','+ 
            line_pieces[4] +','+ line_pieces[5] +','+ line_pieces[6] + '\n')
raw_file.close()
processed_file.close()

print("Converted File for Performance: " + datestring + ", saved to " + output_filename)

#0 80.557930047 
#1 /metatone/touch 
#2 2678456D-9AE7-4DCC-A561-688A4766C325 
#3 934 
#4 215 
#5 0 
#6 10.0.1.4 
#7 57120