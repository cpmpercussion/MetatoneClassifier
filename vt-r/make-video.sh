#!/bin/bash

data_frame=$1
plotter_name=$2
split_cols=$3
window_length=$4
window_lag=$5
alpha=$6
speedup=$7

frame_path=video/${plotter_name}/${window_length}sec
rate=$(echo "scale=0; $speedup/$window_lag" | bc -l)

if [ ! -d "$frame_path" ]; then
    mkdir -p $frame_path
    echo mkdir -p $frame_path
fi

eval R CMD BATCH --vanilla \'--args df.name=\"${data_frame}\" plotter.name=\"${plotter_name}\" split.cols=${split_cols} window.length=${window_length} window.lag=${window_lag} alph=${alpha}\' make-frames.r ${frame_path}/R.out

wait

ffmpeg -y -r $rate -i ${frame_path}/%5d.png -s hd1080 -vcodec libx264 -vpre libx264-lossless_slower ${frame_path}/${plotter_name}-${window_length}s.mp4
