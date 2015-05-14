"""
Create a CSV Coding form for Ensemble Metatone videos.
"""
from datetime import timedelta
from datetime import datetime
from datetime import time
import subprocess
import argparse
import math

parser = argparse.ArgumentParser(description='Create a CSV Coding form for Ensemble Metatone videos.')
parser.add_argument('filename',help='Video file used to create a coding form.')

args = parser.parse_args()

video_filename = args.filename

def getLength(filename):
  result = subprocess.Popen(["ffprobe", filename],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
  length = [x for x in result.stdout.readlines() if "Duration" in x][0].replace(',','').replace('  ',' ').split()[1]
  length = length.split(':')
  hours = int(length[0])
  minutes = int(length[1])
  seconds = int(math.floor(float(length[2])))
  micro = int((float(length[2]) % 1) * 1000000)
  return time(hours,minutes,seconds,micro)


#video_filename = '/Volumes/cpm-projectdrive/temp/Metatone 20130504 Set 2 - 4K.mov'


if (len(video_filename)>0):
    print("Creating form for " + video_filename + "...")
    
    log_filename = video_filename[:len(video_filename) -4] + '-log.CSV'
    video_length = getLength(video_filename)
    window_size = timedelta(seconds = 5)
    time_stamp = datetime(1,1,1,0,0,0)
    
    header = 'time,charles,christina,yvonne,jonathan\n'
    line_template = ',,,,\n'
    
    log_file = open(log_filename,'w')
    log_file.write(header)
    while (time_stamp.time() < video_length):
        log_file.write(str(time_stamp.minute) + ":" + str(time_stamp.second) + line_template)
        time_stamp = time_stamp + window_size
    log_file.close()
else:
    print("Cannot create form.")




