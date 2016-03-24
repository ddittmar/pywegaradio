#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
print ("start")
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("KeyboardInterrupt")  # on Ctrl+c

print("exit")  # normal exit
