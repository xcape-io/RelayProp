#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GuizeroProp.py
MIT License (c) Marie Faure <dev at faure dot systems>

Add guizero and Tkinter to PropApp.
"""

from constants import *

import os, platform, sys, signal, yaml

from PropApp import PropApp
from guizero import App


class GuizeroProp(PropApp):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self._gui = App(WINDOW_TITLE)

        self._relaunched = False

        if platform.system() != 'Windows':
            signal.signal(signal.SIGUSR1, self.receiveSignal)

        self._gui.tk.after(500, self.poll) # for signals

        self.addPeriodicAction("send all data", self.sendAllDataPeriodically, PUBLISHALLDATA_PERIOD)
        self._gui.tk.after(1, self._startPeriodicTasks) # when derived class is built

    # __________________________________________________________________
    def _startPeriodicTasks(self):
        # Periodic actions
        for title, (func, time) in self._periodicActions.items():
            try:
                self._gui.tk.after(0, func)
                self._logger.info("Periodic task created '{0}' every {1} seconds".format(title, time))
            except Exception as e:
                self._logger.error("Failed to create periodic task '{0}'".format(title))
                self._logger.debug(e)

    # __________________________________________________________________
    def loop(self):
        # guizero loop
        self._gui.display()

    # __________________________________________________________________
    def onConnect(self, client, userdata, flags, rc):
        # extend as a virtual method
        self.sendAllData()

    # __________________________________________________________________
    def onDisconnect(self, client, userdata, rc):
        # extend as a virtual method
        if self._relaunched:
            self._relaunched = False
            try:
                self._mqttClient.connect_async(self._mqttServerHost, port=self._mqttServerPort, keepalive=MQTT_KEEPALIVE)
            except Exception as e:
                self._logger.error("MQTT API : failed to call connect_async()")
                self._logger.debug(e)

    # __________________________________________________________________
    def onMessage(self, topic, message):
        # extend as a virtual method
        print(topic, message)
        if message == "app:startup":
            self.sendAllData()
            self.sendDone(message)
        elif message == "app:quit":
            self.sendAllData()
            self.sendDone(message)
            self.quit()
        else:
            self.sendOmit(message)

    # __________________________________________________________________
    def playInSeconds(self, func, time):
        try:
            self._gui.tk.after(int(time*1000), func)
        except Exception as e:
            self._logger.error("Failed to replay in {} seconds".format(time))
            self._logger.debug(e)

    # __________________________________________________________________
    def poll(self):
        # required for Tkinter to catch signal quickly
        self._gui.tk.after(500, self.poll)

    # __________________________________________________________________
    def quit(self):
        self._gui.exit_full_screen()
        self._gui.destroy()
        try:
            self._mqttClient.disconnect()
            self._mqttClient.loop_stop()
        except:
            pass
        sys.exit(0)

    # __________________________________________________________________
    def receiveSignal(self, signalNumber, frame):
        if signalNumber == signal.SIGUSR1:
            self.relaunch()

    # __________________________________________________________________
    def relaunch(self):
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as conffile:
                self._config = yaml.load(conffile, Loader=yaml.SafeLoader)
        print(self._config)
        if 'host' in self._config:
            self._mqttServerHost = self._config['host']
        if 'port' in self._config:
            self._mqttServerPort = self._config['port']
        self._relaunched = True
        self._mqttClient.disconnect()
        try:
            self._mqttClient.connect_async(self._mqttServerHost, port=self._mqttServerPort, keepalive=MQTT_KEEPALIVE)
        except Exception as e:
            self._logger.error("MQTT API : failed to call connect_async()")
            self._logger.debug(e)

    # __________________________________________________________________
    def sendAllDataPeriodically(self):
        self.sendAllData()
        self.playInSeconds(self.sendAllDataPeriodically, PUBLISHALLDATA_PERIOD)
