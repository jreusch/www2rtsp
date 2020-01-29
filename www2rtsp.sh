#!/bin/sh

mydir=`dirname $(readlink -f $0)`
export PYTHONPATH=$mydir/src

python3 -m WWW2RTSP.websource "$@"
