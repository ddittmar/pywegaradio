#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def my_excepthook(type, value, traceback):
    logger.error("Uncaught exception!", exc_info=(type, value, traceback))


sys.excepthook = my_excepthook

#raise RuntimeError('This is the error message')

try:
    raw_input("Wait for input\n")
except KeyboardInterrupt:
    print "Ctrl+C"
