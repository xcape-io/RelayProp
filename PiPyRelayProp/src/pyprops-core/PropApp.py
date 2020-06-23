#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PropApp.py
MIT License (c) Faure Systems <dev at faure dot systems>

Props base class extends MqttApp:
- add automation
- agnostic to asyncio, Qt, Tkinter or Kivy
- add methods to support Room protocol like ArduinoProps
    DATA -> send variables to control
    MESG -> send text to display in control
    DONE -> acknowledge that a command has been performed
    OMIT -> acknowledge that a command has been ignored
    OVER -> notify that a challenge is over
    REQU -> request a command to another props
    PROG -> request a control program
"""

from constants import *
from MqttApp import MqttApp


class PropApp(MqttApp):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self._periodicActions = {}

    # __________________________________________________________________
    def addData(self, data):
        self._publishable.append(data)

    # __________________________________________________________________
    def addPeriodicAction(self, title, func, time):
        if title in self._periodicActions:
            self._logger.warning("Duplicate periodic action ignored '{0}' every {1} seconds".format(title, time))
        else:
            self._periodicActions[title] = (func, time)
            self._logger.info("New periodic action added '{0}' every {1} seconds".format(title, time))

    # __________________________________________________________________
    def removeData(self, data):
        self._publishable.remove(data)

    # __________________________________________________________________
    def sendAllData(self):
        self._publishAllData()

    # __________________________________________________________________
    def sendDataChanges(self):
        self._publishDataChanges()

    # __________________________________________________________________
    def sendData(self, data):
        self._publishMessage(self._mqttOutbox, "DATA " + data)

    # __________________________________________________________________
    def sendDone(self, action):
        self._publishMessage(self._mqttOutbox, "DONE " + action)

    # __________________________________________________________________
    def sendMesg(self, message, topic=None):
        if topic is None:
            self._publishMessage(self._mqttOutbox, "MESG " + message)
        else:
            self._publishMessage(topic, "MESG " + message)

    # __________________________________________________________________
    def sendOmit(self, action):
        self._publishMessage(self._mqttOutbox, "OMIT " + action)

    # __________________________________________________________________
    def sendOver(self, challenge):
        self._publishMessage(self._mqttOutbox, "OVER " + challenge)

    # __________________________________________________________________
    def sendProg(self, program):
        self._publishMessage(self._mqttOutbox, "PROG " + program)

    # __________________________________________________________________
    def sendRequ(self, request, topic=None):
        if topic is None:
            self._publishMessage(self._mqttOutbox, "REQU " + request)
        else:
            self._publishMessage(topic, "REQU " + message)
