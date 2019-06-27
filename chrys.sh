#!/bin/bash
/usr/bin/streamer -t 100 -r 0.4 -s 1280x720 -o /home/pi/timelapse/images/timelapse0000.jpeg &&
/usr/bin/gst-launch-1.0 multifilesrc location=/images/timelapse%04d.jpeg index=1 caps=“image/jpeg,framerate=24/1” ! jpegdec ! x264enc ! mp4mux ! filesink location=/home/pi/timelapse/video/$(date +%m%d_%H%M%S).mp4
sync
