#!/usr/bin/python
from time import sleep
import os
""" copies touch files into the Processing app's path, then runs the app"""
SLEEP_TIME = 1800
open_app_command = "open MetatoneTouchLogPlayer/application.macosx/MetatoneTouchLogPlayer.app"
input_csv = "MetatoneTouchLogPlayer/application.macosx/MetatoneTouchLogPlayer.app/Contents/Java/data/input.csv"

print("Find all the touch files.")
touch_files = []
for local_file in os.listdir("touch-files"):
        if local_file.endswith("-touches.csv"):
            touch_files.append("touch-files/" + local_file)
print(str(touch_files))

print("Now going to run the app for each one!!")
for touch_file in touch_files:
    print(touch_file)
    os.system("rm " + input_csv)
    os.system("cp " + touch_file + " " + input_csv)
    os.system(open_app_command)
    print("Now sleeping for 30mins.")
    sleep(SLEEP_TIME)
print("All done! bye!")
