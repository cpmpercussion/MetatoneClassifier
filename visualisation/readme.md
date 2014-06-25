# FFMPEG Command

Here's the ffmpeg command to get the visualisation right...

    ffmpeg -f image2 -framerate 25 -i %06d.tga -vcodec qtrle -r 25 output.mov