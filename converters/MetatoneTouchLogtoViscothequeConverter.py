"""
Script to convert a metatone touch log to Ben Swift's Viscotheque logging format (not used...)
"""
import pandas as pd
import numpy as np

#data = array([])

#test = "152.146475138 [ /metatone/touch, 6769FE40-5F64-455B-82D4-814E26986A99, 938.5, 696, 0 ] a NetAddr(10.0.1.6, 57120)"
#test = test.replace("[","")
#test = test.replace("]","")
#test = test.replace(",","")
#test = test.replace("a NetAddr(","")
#test = test.replace(")","")
#test = test.replace("  "," ")
#test.split()

#input_filename = '/Users/charles/Dropbox/Metatone/20130420/MetatoneOSCLog-20130420-14h55'
#input_filename = '/Users/charles/Dropbox/Metatone/20130421/MetatoneOSCLog-20130421-11h38'
#input_filename = '/Users/charles/Dropbox/Metatone/20130427/MetatoneOSCLog-20130427-17h29.txt'
#input_filename = '/Users/charles/Dropbox/Metatone/20130504/MetatoneOSCLog-20130504-12h12'
input_filename = '/Users/charles/Dropbox/Metatone/20130504/MetatoneOSCLog-20130504-14h23'


output_filename = input_filename + '-touches-vtversion.csv'

raw_file = open(input_filename, 'r')
processed_file = open(output_filename,'w')
#first_time = 14.837146462

device_names = {
    '2678456D-9AE7-4DCC-A561-688A4766C325':'1',
    '97F37307-2A95-4796-BAC9-935BF417AC42':'2',
    '6769FE40-5F64-455B-82D4-814E26986A99':'3',
    '1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930':'4'}


processed_file.write('\"time\",\"uid\",\"gid\",\"mode\",\"x\",\"y\"\n')

for line in raw_file:
    line = line.replace("[","")
    line = line.replace("[","")
    line = line.replace("]","")
    line = line.replace(",","")
    line = line.replace("a NetAddr(","")
    line = line.replace(")","")
    line = line.replace("  "," ")
    line_pieces = line.split()
    if (line_pieces[1] == "/metatone/touch"):
        # write the line...
        processed_file.write(line_pieces[0] +','+ device_names[line_pieces[2]]
            +','+ '1,1,'+str(float(line_pieces[3])/1024.0) +','+ str(float(line_pieces[4])/768.0) +','+'\n')
        #processed_file.write(line)
raw_file.close()
processed_file.close()

#0 80.557930047 
#1 /metatone/touch 
#2 2678456D-9AE7-4DCC-A561-688A4766C325 
#3 934 
#4 215 
#5 0 
#6 10.0.1.4 
#7 57120