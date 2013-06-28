#!/bin/bash

cat $1 | while read line; do
    ./make-video.sh $line &
done
