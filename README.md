# ChrysalisCam
Programmatically generate tiny timelapse videos using a Pi and a webcam, then fling those videos into the DropBox cloud.
This is a guide to making automated timelapse videos using a Raspberry Pi and a webcam. This project incorporates [Andrea Fabrizi's Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader), and is a spiritual successor to/cribs instructional format & some wordage from [Nicole He's Grow_Slow](https://github.com/nicolehe/grow_slow), without whom it probably wouldn't exist.

This project is appropriate for people who have done very little coding.

![](/butterfly.gif)

It was originally created to monitor a Chrysalis > Butterfly kit in a public library setting, which is why many of the file names have a butterfly theme (although I suppose it could also be post-apocalypse psychic children theme).

This set of instructions are particularly suited to the following scenarios:
* you want to use a Pi and a webcam to periodically create tiny programmatically generated timelapse videos
* multiple people would like instant access to the programmatically generated videos, but it's not appropriate for said people to all have SSH access to the Pi
* you don't want to broadcast the results on something like Twitter
* you DO want to broadcast the results on Twitter but you would also like cloud backup of your files

Obviously you can mix and match to take what you need from it!

## Things You Need

* Raspberry Pi 3B+
* USB Webcam
* External monitor
* External keyboard & mouse
* HDMI cable
* Dropbox developer account

## 1. Setting up your Pi

[Follow this guide]("https://www.raspberrypi.org/help/quick-start-guide/) to set up your Pi for the first time. You'll need to plug it in to your monitor with your HDMI cable, and plug in your keyboard and mouse. [Connect your Pi](https://www.raspberrypi.org/documentation/configuration/wireless/) to your WiFi network.

## 2. Setting the date

Open the Terminal.

`@raspberrypi ~ $`

We need to set the date:

`date`

If you don't get the correct date and time stamp back, enter:

`tzselect`

Follow the instructions to set your timezone, and confirm it by entering `date` again.

## 3. Set up image capture and video pipeline

We'll be loosely following [these instructions](https://www.raspberrypi.org/forums/viewtopic.php?t=72435/). We need to capture still images, and then render those images into a video file.

First we have to install the streamer module via Terminal:

`sudo apt-get install streamer`

Second, we'll install gstreamer module with so that we can render the final video using the Raspberry Pi's GPU.

`sudo apt-get install gstreamer1.0-tools`

Check the installation to make sure it has the codecs you need:

`gst-inspect-1.0 | grep x264enc`

`gst-inspect-1.0 | grep mp4mux`

`gst-inspect-1.0 | grep jpegdec`

You should see the tools above listed.

## 4. Make your file directory

Let's keep things neat and tidy by creating a file directory just for this project. You can call your files and folders whatever you like, but it's extremely important to match directory names and case across all of your code, so keep that in mind when your create your file structure.

`mkdir /home/pi/timelapse`

`mkdir /home/pi/timelapse/images`

`mkdir /home/pi/timelapse/videos`

Great! Now let's go hang out in our new timelapse folder and run some tests:

`cd /home/pi/timelapse/`

Your Terminal should now look something like this:

`pi@raspberrypi:~/timelapse $`

## 5. Test: Capture your images and programmatically create a video

We're going to run a quick test to make sure our modules work:

`streamer -t 20 -r 0.4 -s 1280x720 -o /images/timelapse0000.jpeg`

* -t 20 = the number of frames you want to capture
* -r 0.4 = frame rate (0.4 fps or 2.5 seconds/frame)
* -s 1280x720 = resolution

Hit enter. The camera should immediately capture a set of 20 images in /home/pi/timelapse/images.

Time to encode these into a video!

`gst-launch-1.0 multifilesrc location=/images/timelapse%04d.jpeg index=1 caps=“image/jpeg,framerate=24/1” ! jpegdec ! x264enc ! mp4mux ! filesink location=/timelapse/videos/timelapse.mp4`

The video should be created immediately - only 20 images means this will happen very fast. We'll guard against data corruption by adding in:

`sync`

A few things to keep in mind:

* jpegdec decodes our JPEG images. Note that there's no difference between a JPG and a JPEG, but the pipeline will not work if the two extensions don't match. If all your images are .jpg instead of .jpeg, you must change every reference to JPEG to JPG in the pipeline code above.
* Fun fact: every JPG image is built in 8x8 bit blocks. Not so fun fact: if any of your images have been cropped or saved in a non-standard resolution that is not divisible by 8, the pipeline will not work. 1280x720 works great. 1270x720 does not.
* We've asked the pipeline for a video that is compressed with a .264 codec - x264enc - and specified an MP4 container with MP4mux. MP4 works great with most services, including the Twitter API, which is why we're using it. You could change the code above to ask for an AVI file instead by changing your codecs and muxers like so:

`gst-launch-1.0 multifilesrc location=timelapse%04d.jpeg index=1 caps="image/jpeg,framerate=24/1" ! jpegdec ! omxh264enc ! avimux ! filesink location=timelapse.avi`

## 6. Dropbox-Uploader
Did you know that Raspberry Pis use an ARM processor? They do! Did you know that DropBox clients only support x86-based computers and not ARM-based ones? Alas, it's true. Luckily some enterprising individuals have created beautiful code that we can use to access the DropBox API on the Raspberry Pi.

Visit [this page](https://github.com/andreafabrizi/Dropbox-Uploader) for the Dropbox Uploader BASH script. This is where you'll need a Dropbox developer account. Follow the instructions and then come back! Make sure the dropbox_uploader.sh script is either copied into your project folder and/or that you use an absolute file path in our autodropbox.py script in step 8.

## 7. SH that Chrys

Save the [chrys.sh](/chrys.sh) file above to your Pi in /home/pi/timelapse. Alternatively, you can open up the Raw and then paste those into your own self-created file by using the Terminal and typing:

`nano chrys.sh`

 `#!/bin/bash
/usr/bin/streamer -t 100 -r 0.4 -s 1280x720 -o /home/pi/timelapse/images/timelapse0000.jpeg &&
/usr/bin/gst-launch-1.0 multifilesrc location=/images/timelapse%04d.jpeg index=1 caps=“image/jpeg,framerate=24/1” ! jpegdec ! x264enc ! mp4mux ! filesink location=/home/pi/timelapse/video/$(date +%m%d_%H%M%S).mp4
sync`

 chrys.sh will capture 100 images and dump them in /home/pi/timelapse/images, then create an MP4 from those images and save it in /home/pi/timelapse/video with a datestamped filename. Each time the script runs, the images will be overwritten - only the video will remain.

A few notes:
* We use && to tell the program to successfully finish taking the images BEFORE it moves on to the video pipeline.
* We're using absolute file paths here for both streamer and gst-launch-1.0

 ## 8. Python that DropBox

 Save the [autodropbox.py](/autodropbox.py) file above to your Pi in /home/pi/timelapse. Alternatively, you can open up the Raw and paste those into your own self-created file by using the Terminal and typing:

 `nano autodropbox.py`

autodropbox.py will use the paths you define in the file to fling any new video files into the cloud.

See how we're referencing /dropbox_uploader.sh in autodropbox.py? That's a relative file path, which means it assumes that it will be in the same folder as your autodropbox.py script. Make it so OR change the script above to use an absolute path to the dropbox_uploader.sh location.

## 9. Automate the heck out of it

Here comes our friend cron!

Make sure you're in the main /home/pi location. You can use `cd ..` to navigate up the file directory. Once your Terminal says `pi@raspberrypi:~ $` you are ready to dig into scheduling.

`crontab -e`

This is the structure of the crontab:

```
# m h  dom mon dow   command
# * * * * *  command to execute
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 7) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59)
```

We're going to add a line for the BASH and for python:

`10 */4 * * * /bin/sh /home/pi/chrys.sh`

`30 */4 * * * /usr/bin/py /home/pi/autodropbox.py`

Our BASH will run at 10 minutes past, every four hours; our Dropbox script will run at 30 minutes past, every four hours.

###Optional but recommended: set a reboot

Sometimes, things can get messed up if your Pi is just constantly running forever. Also, some USB cameras have weird compatibility issues that are solved with a simple reboot. I recommend that you add another simple script that reboots your Pi once a day before your script runs so that things are always fresh, as they say.

Make a file called reboot.sh:

`nano reboot.sh`

Type this in the file:

`sudo reboot`

Hit ctrl + x to save and quit. Now, open up your crontab again with `crontab -e` and add a line that runs your reboot script once a day:

`0 10 * * * /home/pi/reboot.sh`

This sets it to reboot at 10:00 am every morning.


## 10. Here comes trouble

Possible issues you might run into:
* Folder, user, or cron permission errors. Are you using sudo when you should?
* Absolute vs. relative file paths. Check that you're in the right directory and that your paths match exactly, including case!
* Cron uses a different environment than the Terminal. It doesn't know the same things, so sometimes you have to alert it to the locations of things like /usr/bin/python to run a script successfully.
* Streamer fails to "finish" with the USB camera, which means every other time, your BASH cron job will trigger but not actually do anything. *I know.* I don't have a fix for that. [This Stack Overflow suggestion](https://stackoverflow.com/questions/46253564/recording-usb-cam-on-raspberry-pi-with-ffmpeg-usb-troubleshooting) temporarily solved my webcam issues, but only for streamer and not with fswebcam. Your mileage may vary!
