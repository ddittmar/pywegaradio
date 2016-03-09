#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
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


def configure_logging():
    with open("logging.json") as logging_json:
        data = json.load(logging_json)
    logging.config.dictConfig(data)
    global logger  # configure a global logger object
    logger = logging.getLogger("daemon")


configure_logging()

logger.info("start")
try:
    while True:
        time.sleep(60)  # sleep 60s
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt")  # on Ctrl+c

logger.info("exit")  # normal exit
