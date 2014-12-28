#!/bin/bash


pushd ~/tmp/timelapse

#
INPUT=todays_video.h264
OUTPUT=$HOME/video_archive/output.mp4
# declare -i TIME
# declare -i STIME
# TIME=$(avconv -i  todays_video.h264 -vcodec copy -acodec copy -f null /dev/null 2>&1| grep 'frame=' | cut -f 2 -d ' ')/25
# TIME=$(stat -c%s $INPUT)/50000/24+10
# STIME=$TIME-5

if [ -e "$OUTPUT" ]; then
    mv $OUTPUT ${OUTPUT}.old
fi

# MP4Box -new -fps 24 -add $INPUT -splitx $STIME:$TIME $OUTPUT
MP4Box -new -fps 24 -add $INPUT $OUTPUT

popd

#
# avconv -i  todays_video.h264 -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep 'frame=' | cut -f 2 -d ' '
