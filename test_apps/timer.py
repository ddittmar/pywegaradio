#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Timer


def hello():
    print "hello timer"


t = Timer(10.0, hello)
t.start()

try:
    raw_input("Press Enter to Stop\n")
except KeyboardInterrupt:
    print "Ctrl+C"

t.cancel()
print "done"
