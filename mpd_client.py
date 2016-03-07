#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mpd import (MPDClient)

# use_unicode will enable the utf-8 mode for python2
# see http://pythonhosted.org/python-mpd2/topics/advanced.html#unicode-handling
client = MPDClient(use_unicode=True)
client.connect("localhost", 6600)

for entry in client.lsinfo("/"):
    print("%s" % entry)
for key, value in client.status().items():
    print("%s: %s" % (key, value))
