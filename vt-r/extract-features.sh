#!/bin/bash

# for f in *.wav; do ~/Projects/Viscotheque/src/ex2/R/extract-features.sh $f 5 5; done

export YAAFE_PATH=/usr/local/yaafe_extensions
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
export PYTHONPATH=$PYTHONPATH:/usr/local/python_packages

file_name=$1
window_length_sec=$2
window_step_sec=$3

window_length_samp=$((44100 * $window_length_sec))
window_step_samp=$((44100 * $window_length_sec))

yaafe.py -r 44100 \
-f "autoCor: AutoCorrelation ACNbCoeffs=1 blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "OBSIR: OBSIR DiffNbCoeffs=2 blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "loudness: Loudness LMode=Total blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "sharpness: PerceptualSharpness blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "spread: PerceptualSpread blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "specFlatness: SpectralFlatness blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "specVariation: SpectralVariation blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "specSlope: SpectralSlope blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "specRolloff: SpectralRolloff blockSize=$window_length_samp stepSize=$window_step_samp" \
-f "ZCR: ZCR blockSize=$window_length_samp stepSize=$window_step_samp" \
-o csv -p Precision=8 -p Metadata=False \
$file_name

# -f "onsets: ComplexDomainOnsetDetection blockSize=$(($window_length_samp / 50)) stepSize=$(($window_step_samp / 50)) > StatisticalIntegrator NbFrames=50 StepNbFrames=50" \
