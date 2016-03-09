#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import argparse
import os
import logging
import logging.config

from mpd import (MPDClient)


class MusicDaemonClient(object):
    """
    Class to control the MusicPlayerDaemon
    """

    def __init__(self, mpd_host, mpd_port):
        """
        :param mpd_host: The name of the host (e.g. localhost)
        :param mpd_port: The port of the daemon (e.g. 6600)
        """
        self.log = logging.getLogger("musicDaemonClient")
        self.client = MPDClient(use_unicode=True)
        self.client.connect(mpd_host, mpd_port)
        self.log.debug("mpd connected at {}:{}".format(mpd_host, mpd_port))

    def shutdown(self):
        """
        Shut down this instance. The instance is not usable after this call!
        """
        self.log.debug("shutdown")
        self.client.stop()  # stop playing
        self.client.clear()  # clear queue
        self.client.disconnect()  # disconnect from mpd


def configure_logging(logging_conf_filename):
    with open(logging_conf_filename) as logging_json:
        data = json.load(logging_json)
    logging.config.dictConfig(data)


def load_config():
    parser = argparse.ArgumentParser(description="pyWegaRadio")
    parser.add_argument("-c", "--config", help="filename of the application config (JSON)", required=True)
    args = parser.parse_args()
    with open(args.config) as application_config:
        cfg = json.load(application_config)
    # setting defaults
    cfg['mpd_host'] = cfg['mpd_client'] if 'mpd_host' in cfg else 'localhost'
    cfg['mpd_port'] = cfg['mpd_port'] if 'mpd_port' in cfg else 6600
    return cfg


if __name__ == '__main__':
    config = load_config()
    configure_logging(os.path.dirname(__file__) + '/' + config['logging'])
    log = logging.getLogger("daemon")

    log.info("start...")

    musicClient = MusicDaemonClient(config['mpd_host'], config['mpd_port'])
    # TODO hier noch GPIO hoch fahren
    try:
        while True:
            time.sleep(300)  # sleep in seconds
            log.debug("still alive...")
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt")  # on Ctrl+c

    log.info("shutting down")  # normal exit
    musicClient.shutdown()
    log.info("done...")
