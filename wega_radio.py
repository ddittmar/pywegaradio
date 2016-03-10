#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.client.connect(mpd_host, mpd_port)
        self.log.debug("mpd connected at {}:{}".format(mpd_host, mpd_port))

    def stop(self):
        """
        stop playback
        """
        self.log.debug("stop playback and clear the queue")
        self.client.stop()  # stop playing
        self.client.clear()  # clear queue

    def play(self, uri):
        """
        start playback
        :param uri: the uri to play
        """
        self.stop()
        self.log.debug("play: {}".format(uri))
        self.client.add(uri)
        self.client.play()

    def teardown(self):
        """
        teardown this instance. The instance is unusable after this call!
        """
        self.log.debug("teardown")
        self.stop()
        self.client.disconnect()  # disconnect from mpd


class GpioClient:
    """
    Client for the GPIO stuff
    """

    def __init__(self):
        self.log = logging.getLogger("GpioClient")
        GPIO.setmode(GPIO.BCM)

    def add_input_channel_callback(self, channel, rise_fall, callback):
        """
        Set the specified channel as input channel and adds a callback
        :param channel: the number of the GPIO channel (BCM)
        :param rise_fall: fire the callback at a rising edge or a falling edge
        :param callback: the callback to fire
        """
        self.log("add input channel callback for channel: {}".format(channel))
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
        self.gpioClient.add_input_channel_callback(WegaRadioControl.SWITCH_OFF_GPIO_CHANNEL, GPIO.FALLING,
                                                   self._switch_off_callback)

    def _setup_stations(self, stations):
        """
        Setup the stations
        :param stations: a list with stations
        """
        self.log.debug("setup stations")

        if len(stations) > 4:
            self.log.warn("You defined more than 4 stations. I only setup the first 4 stations in your list.")
        if len(stations) < 4:
            self.log.warn("You defined less than 4 stations. I setup the buttons von left to right with your {}"
                          " stations".format(len(stations)))

        num_stations = 4 if len(stations) >= 4 else len(stations)
        for i in range(num_stations):
            ch = WegaRadioControl.RADIO_GPIO_CHANNELS[i]
            self.gpioClient.add_input_channel_callback(ch, GPIO.RISING, self._switch_to_station)
            self.stations[ch] = stations[i]

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
        self.log.debug("teardown")
        self.mpdClient.teardown()
        self.gpioClient.teardown()


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
    config = load_config()
    logging.config.dictConfig(config['logging'])  # configure logging

    # get the global "deamon" logger
    log = logging.getLogger("daemon")

    log.info("start main loop...")
    radioControl = WegaRadioControl()
    try:
        while True:
            time.sleep(300)  # sleep in seconds
            log.debug("still alive...")
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt")  # on Ctrl+C

    log.info("shutting down")  # normal exit
    radioControl.teardown()
    log.info("exit main loop...")
