#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import logging.config


def configure_logging():
    """
    configures logging for this script
    """
    with open("logging.json") as logging_json:
        data = json.load(logging_json)
    logging.config.dictConfig(data)
    global logger  # configure a global logger object
    logger = logging.getLogger("daemon")


configure_logging()

logger.info("start")
try:
    raw_input()
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt")  # on Ctrl+c

logger.info("exit")  # normal exit
