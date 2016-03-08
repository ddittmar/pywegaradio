#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import logging.config


def config_logging():
    """
    configures logging for this script
    """
    with open("logging.json") as logging_json:
        data = json.load(logging_json)
    logging.config.dictConfig(data)
    global logger  # configure a global logger object
    logger = logging.getLogger("simpleExample")


config_logging()

logger.debug("foooooooooooooo!")
