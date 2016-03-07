#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import RPi.GPIO
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by"
          " using 'sudo' to run your script")
# import mpd
from mpd import (MPDClient)


# use_unicode will enable the utf-8 mode for python2
# see http://pythonhosted.org/python-mpd2/topics/advanced.html#unicode-handling
client = MPDClient(use_unicode=True)
pause_state = 0


def cleanup():
    client.stop()  # stop playing
    client.clear()  # clear queue
    client.disconnect()  # disconnect from mpd
    GPIO.cleanup()


def setup_mpd():
    client.connect("localhost", 6600)
    print "mpd connected!"
    client.clear()  # clear the play queue
    song_id = client.addid('Captain Future/Originalmusik aus der TV-Serie von Christian Bruhn/01_Captain Future.mp3', 0)
    print "Song added with ID: {}".format(song_id)
    print "Playlist: {}".format(client.playlist())


def on_event(channel):
    print "on_event({})".format(channel)
    global pause_state
    pause_state = 1 if pause_state == 0 else 0
    print "pause: {}".format(pause_state)
    client.pause(pause_state)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(17, GPIO.BOTH, callback=on_event, bouncetime=300)


setup_mpd()  # setup mpd client
setup_gpio()

client.play()
client.pause(1)

print 'ready... (Press Enter to exit)'
try:
    raw_input()
except KeyboardInterrupt:
    cleanup()  # on Ctrl+c

cleanup()  # normal exit
