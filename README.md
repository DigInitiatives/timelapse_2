# TimelapseBoogaloo
Take a photo every two minutes, fling the photos into the DropBox cloud, then programatically generate a timelapse video.
This is a guide to making automated timelapse videos using a Raspberry Pi and a webcam. This project incorporates [Andrea Fabrizi's Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader), and is a spiritual successor to/cribs instructional format & some wordage from [Nicole He's Grow_Slow](https://github.com/nicolehe/grow_slow), without whom it probably wouldn't exist.

This project is appropriate for people who have done very little coding.

![](/butterfly.gif)

It was originally created to monitor a Chrysalis > Butterfly kit in a public library setting, which is why many of the file names have a butterfly theme (although I suppose it could also be post-apocalypse psychic children theme).

This set of instructions are particularly suited to the following scenarios:
* you want to use a Pi and a webcam to periodically create tiny programmatically generated timelapse videos
* multiple people would like instant access to the programmatically generated videos, but it's not appropriate for said people to all have SSH access to the Pi
* you don't want to broadcast the results on something like Twitter
* you DO want to broadcast the results on Twitter but you would also like cloud backup of your files
* you want the flexiblity of retaining your original image files for future GIFs and timelapse videos

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

## 3. Set up the webcam

In order to get the webcam working with the Pi, we're going to install a package called `fswebcam`:

`sudo apt-get install fswebcam`

With the USB camera plugged in, we can very easily take photos via the command line:

`fswebcam test.jpg`

Now, if you click on File Manager, you'll see that in your /home/pi directory, you have a file called test.jpg

## 4. Make your file directory

Let's keep things neat and tidy by creating a file directory just for this project. You can call your files and folders whatever you like, but it's extremely important to match directory names and case across all of your code, so keep that in mind when your create your file structure.

`mkdir /home/pi/boogaloo`

`mkdir /home/pi/boogaloo/images`

Great! Now let's go hang out in our new folder:

`cd /home/pi/boogaloo/`

Your Terminal should now look something like this:

`pi@raspberrypi:~/boogaloo $`

## 5. Python that Chrys

Save the [chrys.py](/chrys.py) file above to your Pi in /home/pi/timelapse. Alternatively, you can open up the Raw and then paste those into your own self-created file by using the Terminal and typing:

`nano chrys.py`

It includes this line:

`fswebcam -d/dev/video0 -r 1280x960 -S 20 -l 120 --no-banner /home/pi/timelapse2/frames/Chrys-%Y-%m-%d--%H-%M-%S.jpeg`

Some things to note:
* -S 20 tells the webcam to capture and discard 20 frames – this helps it adjust to light levels. You can edit the script to change this number
* -l 120 (that’s a lowercase L ) tells the webcam to take a photo every 120 seconds, on a loop. The Pi gets a little fussy if this happens more frequently. The loop will tell the script to keep on taking a photo, forever. It's going to be a lot of photos.

## 6. Dropbox-Uploader
Did you know that Raspberry Pis use an ARM processor? They do! Did you know that DropBox clients only support x86-based computers and not ARM-based ones? Alas, it's true. Luckily some enterprising individuals have created beautiful code that we can use to access the DropBox API on the Raspberry Pi.

Visit [this page](https://github.com/andreafabrizi/Dropbox-Uploader) for the Dropbox Uploader BASH script. This is where you'll need a Dropbox developer account. Follow the instructions and then come back! Make sure the dropbox_uploader.sh script is either copied into your project folder and/or that you use an absolute file path in our autodropbox.py script in the next step.

 ## 7. Python that DropBox

 Save the [autodropbox.py](/autodropbox.py) file above to your Pi in /home/pi/timelapse. Alternatively, you can open up the Raw and paste those into your own self-created file by using the Terminal and typing:

 `nano autodropbox.py`

autodropbox.py will use the paths you define in the file to fling any new images into the cloud.
 
 `./dropbox_uploader.sh -s upload /home/pi/boogaloo/images/ .`

See how we're referencing /dropbox_uploader.sh in autodropbox.py? That's a relative file path, which means it assumes that it will be in the same folder as your autodropbox.py script. Make it so OR change the script above to use an absolute path to the dropbox_uploader.sh location.


## 8. Automate the heck out of it

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

We're going to add a line for both our scripts:

`@reboot usr/bin/py /home/pi/boogaloo/chrys.py`

`30 */4 * * * /usr/bin/py /home/pi/boogaloo/autodropbox.py`

Our chrys.py script will start up on reboot and run until someone manually stops it; our Dropbox script will run at 30 minutes past, every four hours.

### Optional but recommended: set a reboot

Sometimes, things can get messed up if your Pi is just constantly running forever. Also, some USB cameras have weird compatibility issues that are solved with a simple reboot. I recommend that you add another simple script that reboots your Pi once a day before your script runs so that things are always fresh, as they say.

Make a file called reboot.sh:

`nano reboot.sh`

Type this in the file:

`sudo reboot`

Hit ctrl + x to save and quit. Now, open up your crontab again with `crontab -e` and add a line that runs your reboot script once a day:

`0 10 * * * /home/pi/reboot.sh`

This sets it to reboot at 10:00 am every morning.

### Optional but recommended: auto-delete old files

Listen, the Pi does not have that much space. This isn't a big deal if you're planning to take a short timelapse, but if you're thinking of a project that will stretch on for weeks without your intervention, it's just easier to auto-delete old images that have already been uploaded to the cloud.

Add this line to your crontab:


## 9. Prepare yourself for videos

All right, you have several thousand beautiful images and you want them to be a timelapse video. Open up your Terminal.

First we have to make sure that our images match our pipeline paramaters. This is what we'll be using:

`gst-launch-1.0 multifilesrc location=/boogaloo/finalcountdown/boogaloo%01d.jpeg index=1 caps=“image/jpeg,framerate=24/1” ! jpegdec ! x264enc ! mp4mux ! filesink location=/boogaloo/timelapse.mp4`

A couple things to keep in mind:

* jpegdec decodes our JPEG images. Note that there's no difference between a JPG and a JPEG, but the pipeline will not work if the two extensions don't match. If all your images are .jpg instead of .jpeg, you must change the filename reference from JPEG to JPG in the pipeline code above.
* Fun fact: every JPG image is built in 8x8 bit blocks. Not so fun fact: if any of your images have been cropped or saved in a non-standard resolution that is not divisible by 8, the pipeline will not work. 1280x720 works great. 1270x720 does not.

Let's swing back around to file names. Do your image filenames match your pipeline code? No? Let's do a quick cleanup to make our lives easier. Collect all your images together in a single folder. If you still want a timestamped version, keep a copy of the originals somewhere else. Open up terminal and navigate to your desired folder full of images:

`cd /home/pi/boogaloo/finalcountdown`

Paste this line into the Terminal:

`awk 'BEGIN { for (i=1; i<ARGC; i++) system("mv -v " ARGV[i] " " i ".jpg")}' *.jpg`

This will rename all images in our /finalcountdown folder to a sequential number, starting with 1.jpg. Because we're starting with 1.jpg instead of 0001.jpg, swap out %04d for %01d.

## 10. Make a video!

Your images all have beautiful sequential names. Time to use Terminal to programmatically turn them into a timelapse video! 

`gst-launch-1.0 multifilesrc location=/boogaloo/finalcountdown/boogaloo%01d.jpg index=1 caps=“image/jpeg,framerate=24/1” ! jpegdec ! x264enc ! mp4mux ! filesink location=/boogaloo/timelapse.mp4`

We've asked the pipeline for a video that is compressed with a .264 codec - x264enc - and specified an MP4 container with MP4mux. MP4 works great with most services, including the Twitter API, which is why we're using it. You could change the code above to ask for an AVI file instead by changing your codecs and muxers like so:

`gst-launch-1.0 multifilesrc location=timelapse%04d.jpg index=1 caps="image/jpeg,framerate=24/1" ! jpegdec ! omxh264enc ! avimux ! filesink location=timelapse.avi`

Depending on how many images you've got, this could take a while. We'll guard against data corruption by adding in:

`sync`

## 11. Here comes trouble

Possible issues you might run into:
* Folder, user, or cron permission errors. Are you using sudo when you should?
* Absolute vs. relative file paths. Check that you're in the right directory and that your paths match exactly, including case!
* Cron uses a different environment than the Terminal. It doesn't know the same things, so sometimes you have to alert it to the locations of things like /usr/bin/python to run a script successfully.
* fswebcam fails to "finish" with the USB camera, which means every other time, your cron job will trigger but not actually do anything. *I know.* I don't have a fix for that. [This Stack Overflow suggestion](https://stackoverflow.com/questions/46253564/recording-usb-cam-on-raspberry-pi-with-ffmpeg-usb-troubleshooting) temporarily solved my webcam issues, but only for streamer and not with fswebcam. Your mileage may vary!
