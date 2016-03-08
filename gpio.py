#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by"
          " using 'sudo' to run your script")


def on_click(channel):
    print 'click on {}'.format(channel)


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(17, GPIO.RISING, callback=on_click, bouncetime=200)
print 'ready... (Press Enter to exit)'

try:
    raw_input()
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
