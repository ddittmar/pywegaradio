#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import json
import argparse
import logging
import logging.config

from mpd import (MPDClient)

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by"
          " using 'sudo' to run your script")


class MusicDaemonClient:
    """
    Class to control the MusicPlayerDaemon
    """

    def __init__(self, mpd_host, mpd_port):
        """
        :param mpd_host: The name of the host (e.g. localhost)
        :param mpd_port: The port of the daemon (e.g. 6600)
        """
        self.log = logging.getLogger("MusicDaemonClient")
        self.client = MPDClient(use_unicode=True)

        self.host = mpd_host
        self.port = mpd_port

        # test the mpd connection
        self._connect()
        self._disconnect()

    def _connect(self):
        self.client.connect(self.host, self.port)

    def _disconnect(self):
        self.client.close()
        self.client.disconnect()

    def _stop(self):
        self.client.stop()  # stop playing
        self.client.clear()  # clear queue

    def _play(self, uri):
        self.client.add(uri)
        self.client.play()

    def stop(self):
        """
        stop playback
        """
        self.log.debug("stop playback and clear the queue")
        self._connect()
        self._stop()
        self._disconnect()

    def play(self, uri):
        """
        start playback
        :param uri: the uri to play
        """
        self.log.debug("play: {}".format(uri))
        self._connect()
        self._stop()
        self._play(uri)
        self._disconnect()

    def info(self):
        self._connect()
        try:
            res = dict()
            res['status'] = self.client.status()
            res['stats'] = self.client.stats()
            res['current_song'] = self.client.currentsong()
            return res
        finally:
            self._disconnect()

    def teardown(self):
        """
        teardown this instance. The instance is unusable after this call!
        """
        self.log.debug("teardown")
        self._connect()
        self._stop()
        self._disconnect()

    def mpd_version(self):
        self._connect()
        try:
            return self.client.mpd_version
        finally:
            self._disconnect()


class GpioClient:
    """
    Client for the GPIO stuff
    """

    def __init__(self):
        self.log = logging.getLogger("GpioClient")
        GPIO.setmode(GPIO.BCM)
        self.log.info("RPi.GPIO Version: {}".format(GPIO.VERSION))

    @staticmethod
    def add_input_channel_callback(channel, rise_fall, callback):
        """
        Set the specified channel as input channel and adds a callback
        :param channel: the number of the GPIO channel (BCM)
        :param rise_fall: fire the callback at a rising edge or a falling edge
        :param callback: the callback to fire
        """
        GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(channel, rise_fall, callback=callback, bouncetime=300)

    def teardown(self):
        """
        teardown this instance. GPIO is unusable after this call!
        """
        self.log.debug("teardown")
        GPIO.cleanup()


class WegaRadioControl:
    """
    Controls the WEGA radio
    """

    SWITCH_OFF_GPIO_CHANNEL = 17
    RADIO_GPIO_CHANNELS = [5, 6, 13, 19]

    def __init__(self):
        self.log = logging.getLogger("WegaRadioControl")
        self.mpdClient = MusicDaemonClient(config['mpd_host'], config['mpd_port'])
        self.gpioClient = GpioClient()
        self.stations = dict()

        # configure the station callbacks
        self._setup_stations(config['stations'])

        # register a callback to switch the radio off
        self.log.info(
            "register callback for the 'off' button on channel {}".format(WegaRadioControl.SWITCH_OFF_GPIO_CHANNEL))
        self.gpioClient.add_input_channel_callback(WegaRadioControl.SWITCH_OFF_GPIO_CHANNEL, GPIO.FALLING,
                                                   self._switch_off_callback)

    def _setup_stations(self, stations):
        """
        Setup the stations
        :param stations: a list with stations
        """

        if len(stations) > 4:
            self.log.warn("You defined more than 4 stations. I only setup the first 4 stations in your list.")
        if len(stations) < 4:
            self.log.warn("You defined less than 4 stations. I setup the buttons von left to right with your {}"
                          " stations".format(len(stations)))

        num_stations = 4 if len(stations) >= 4 else len(stations)
        for i in range(num_stations):
            ch = WegaRadioControl.RADIO_GPIO_CHANNELS[i]
            self.stations[ch] = stations[i]
            self.log.info("register callback for '{}' on channel {}".format(stations[i]['name'], ch))
            self.gpioClient.add_input_channel_callback(ch, GPIO.RISING, self._switch_to_station)

    def _switch_off_callback(self):
        """
        Callback function for the off switch
        """
        self.log.info("switch off the radio")
        self.mpdClient.stop()

    def _switch_to_station(self, channel):
        """
        Callback to switch to the station with the given GPIO-Channel
        :param channel: the GPIO-Channel
        """
        station = self.stations[channel]
        self.log.info("switch to station: {}".format(station['name']))
        self.mpdClient.play(station['uri'])

    def teardown(self):
        """
        This instance is unusable after this call!
        """
        self.log.info("teardown")
        self.mpdClient.teardown()
        self.gpioClient.teardown()


class MyLogger:
    """
    Class to redirect stdout und stderr to the logging files
    """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())


def log_mpd_status(music_daemon_client):
    """
    Write the status of the MPD to the log
    :param music_daemon_client: the MusicDaemonClient
    """
    info = music_daemon_client.info()
    log.info("MPD Status: {}".format(info['status']))
    log.info("MPD Stats: {}".format(info['stats']))
    log.info("MPD Current Song: {}".format(info['current_song']))


def load_config():
    """
    load the JSON config file for the application
    :return: the config dictionary
    """
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
    config = load_config()  # load the config file
    logging.config.dictConfig(config['logging'])  # configure logging
    log = logging.getLogger("daemon")  # get the global "daemon" logger

    # Replace stdout with logging to file at DEBUG level
    sys.stdout = MyLogger(log, logging.DEBUG)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(log, logging.ERROR)

    log.info("start...")

    musicDaemonClient = MusicDaemonClient(config['mpd_host'], config['mpd_port'])
    log.info("MPD Version: {}".format(musicDaemonClient.mpd_version()))  # print the version of the daemon
    log_mpd_status(musicDaemonClient)

    radioControl = WegaRadioControl()
    try:
        while True:
            time.sleep(300)  # sleep in seconds
            log.info("still alive...")
            log_mpd_status(musicDaemonClient)
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt: Ctrl+c")  # on Ctrl+C

    radioControl.teardown()
    log.info("exit...")
