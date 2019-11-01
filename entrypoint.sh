#!/bin/bash
set -e
# Run
case "$1" in
    start)
        export IP_ADDR=$(curl -s checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//')
        echo "Dataset preparation"
        python scripts/data_preparation.py --folder /data -s -d
        echo "Training start"
        nohup python scripts/train.py --save_path $SAVE_PATH --sr $SR --hop-length $HOP_LENGTH --win-length $WIN_LENGTH --n-fft $N_FFT &
        tensorboard --logdir=$SAVE_PATH --port=$EXPORT
        echo "done making training block"
esac
