import sys
import os

# this runs the following script from the command line that takes the photo and saves it
# it will only work for USB webcams,
# you'll have to do something different if you're using a pi-cam
# if you find your webcam can't handle light levels use -S xx to specify skip frames before photo capture
# capture a second timestamped photo plant-%Y-%m-%d.jpg to start gathering images for your inevitable timelapse
# -l 120 tells fswebcam to take images every 120 seconds, on a loop, forever
os.system ("fswebcam -d/dev/video0 -r 1280x960 -S 20 -l 120 --no-banner /home/pi/timelapse2/frames/Chrys-%Y-%m-%d--%H-%M-%S.jpg")
