#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import json
import logging
import logging.config


class MyLogger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())


def configure_logging(logging_conf_filename):
    with open(logging_conf_filename) as logging_json:
        data = json.load(logging_json)
    logging.config.dictConfig(data)
    global log  # configure a global logger
    log = logging.getLogger("daemon")

    # Replace stdout with logging to file at DEBUG level
    sys.stdout = MyLogger(log, logging.DEBUG)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(log, logging.ERROR)


# TODO parameter einlesen um die Logging-Config zu finden

configure_logging("logging.json")

log.info("start")
try:
    while True:
        time.sleep(10)  # sleep in seconds
        log.debug("wakeup...")
except KeyboardInterrupt:
    log.info("Interrupt")  # on Ctrl+c

log.info("exit")  # normal exit
