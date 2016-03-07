#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mpd import (MPDClient)


def cleanup():
    client.stop()  # stop playing
    client.clear()  # clear queue
    client.disconnect()  # disconnect from mpd


# use_unicode will enable the utf-8 mode for python2
# see http://pythonhosted.org/python-mpd2/topics/advanced.html#unicode-handling
client = MPDClient(use_unicode=True)
client.connect("localhost", 6600)
print "mpd connected!"

client.clear()  # clear queue

# print client.commands()  # list der Kommandos auf die wir zugriff haben

songId = client.addid('Captain Future/Originalmusik aus der TV-Serie von Christian Bruhn/01_Captain Future.mp3', 0)
print "Song ID: {}".format(songId)
print "Playlist: {}".format(client.playlist())

client.play()
try:
    raw_input("Press Enter to Stop")
except KeyboardInterrupt:
    cleanup()
cleanup()
