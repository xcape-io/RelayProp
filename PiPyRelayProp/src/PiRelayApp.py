#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PiRelayApp.py
MIT License (c) Marie Faure <dev at faure dot systems>

Raspberry Pi Relay Prop extends AsyncioProp.

settings:
    NONE: not loaded
    OFFLINE ERROR: error while loading offline settings
    OFFLINE: loaded from local file
    ONLINE ERROR: error while loading online settings
    OK: loaded form MQTT broker

board:
    Pi: bare Raspberry Pi
    Pi MCP23017: Raspberry Pi with MCP23017 expander
"""

import os
import json
import time
import asyncio

from AsyncioProp import AsyncioProp
from PropData import PropData
from PropPin import PropPin
from constants import *

if USE_GPIO and os.path.isfile('/opt/vc/include/bcm_host.h'):
    import RPi.GPIO as GPIO

try:
    MCP23017_ADDRESS
    from mcp23017 import *
    import smbus
    #bus = smbus.SMBus(1)
except NameError:
    pass


class PiRelayApp(AsyncioProp):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self._pinPropData = {}
        self._propPins = {}

        try:
            MCP23017_ADDRESS
            self._mcp23017 = True
        except NameError:
            self._mcp23017 = False

        if self._mcp23017:
            board_initial = BOARD_PI_MCP23017
        else:
            board_initial = BOARD_PI

        self._board_p = PropData('board', str, board_initial, logger=self._logger)
        self.addData(self._board_p)

        self._settings_p = PropData('settings', str, 'NONE', logger=self._logger)
        self.addData(self._settings_p)

        self._settings_date_p = PropData('settings-date', str, NULL_DATE, logger=self._logger)
        self.addData(self._settings_date_p)

        # no running loop is available at that time so we can't use asyncio.create_task()
        self.addPeriodicAction("read JSON rescue once", self.readJsonRescue, 3)

    # __________________________________________________________________
    def _commandFromAction(self, action):

        if action == '1':
            return GPIO.HIGH
        elif action == '0':
            return GPIO.LOW
        elif action in COMMANDS_SYNONYMS_HIGH:
            return GPIO.HIGH
        elif action in COMMANDS_SYNONYMS_LOW:
            return GPIO.LOW

        return None

    # __________________________________________________________________
    def _gpioLevel(self, gpio):

        if gpio == GPIO_HIGH:
            return GPIO.HIGH
        return GPIO.LOW

    # __________________________________________________________________
    def _parseCommandMessage(self, message):

        predicate, action = message.split(':')
        pins = []
        command = self._commandFromAction(action)

        if command is None:
            return pins, command

        if predicate.endswith('/*'):
            group = predicate[:-1]
            for pin in self._propPins:
                if self._propPins[pin].getVariable().startswith(group):
                    if pin.startswith('MCP23017'):
                        self._logger.info("Pin ignored for '{}' command : {}".format(message, pin))
                    else:
                        try:
                            output = int(pin[4:])
                            pins.append(output)
                        except Exception as e:
                            self._logger.error("Failed to parse '{}' output in : {}".format(pin, message ))
                            self._logger.debug(e)
        else:
            for pin in self._propPins:
                print(pin, self._propPins[pin])
                if self._propPins[pin].getVariable() == predicate:
                    if pin.startswith('MCP23017'):
                        self._logger.info("Pin ignored for '{}' command : {}".format(message, pin))
                    else:
                        try:
                            output = int(pin[4:])
                            pins.append(output)
                        except Exception as e:
                            self._logger.error("Failed to parse '{}' output in : {}".format(pin,message ))
                            self._logger.debug(e)

        return pins, command

    # __________________________________________________________________
    def cleanupGpioPins(self):

        for pin in self._propPins:
            try:
                output = int(pin[4:])
                GPIO.setup(output, GPIO.IN)
                self._logger.info("Cleanup GPIO {} (set as input)".format(output))
            except Exception as e:
                self._logger.error("GPIO cleanup failed for pin {}".format(pin))
                self._logger.debug(e)
        self._pinPropData = {}
        self._propPins = {}

    # __________________________________________________________________
    def onConnect(self, client, userdata, flags, rc):
        # extend as a virtual method
        self.sendAllData()

    # __________________________________________________________________
    def onDisconnect(self, client, userdata, rc):
        # extend as a virtual method
        pass

    # __________________________________________________________________
    def onMessage(self, topic, message):
        # extend as a virtual method
        print(topic, message)
        if topic == self._definitions['mqtt-sub-settings']:
            self.processSettingsMessage(message)
        else:
            if message == "app:startup" or message == "app:data":
                self.sendAllData()
                self.sendDone(message)
            else:
                outputs, command = self._parseCommandMessage(message)
                if command is None:
                    self._logger.warning("Command unknown in : {}".format(message))
                    self.sendOmit(message)
                elif outputs:
                    for gpio in outputs:
                        GPIO.output(gpio, command)
                        self._logger.info("GPIO {} set to {}".format(gpio, command))
                        if gpio in self._pinPropData:
                            self._pinPropData[gpio].update(command)
                        else:
                            self._logger.warning("Prop data noit found for '{}' output".format(gpio))
                    self.sendDataChanges()
                    self.sendDone(message)
                else:
                    self._logger.warning("No output found for : {}".format(message))
                    self.sendOmit(message)

    # __________________________________________________________________
    def processSettingsJson(self, json_list):

        for p in json_list:
            try:
                if self._mcp23017:
                    if p['pin'] == 'GPIO2' or p['pin'] == 'GPIO3':
                        self._logger.info("Pin ignored from settings : {}".format(p))
                    elif p['pin'].startswith('MCP23017'):
                        if self.setMcp23017PinOut(p['pin'], p['initial']):
                            self._propPins[p['pin']] = PropPin(p['pin'], p['variable'], p['initial'], p['alias'])
                            self._logger.info("Pin added from settings : {}".format(p))
                            prop_data = PropData(p['variable'], bool,
                                                 self._gpioLevel(p['initial']),
                                                 alias=p['alias'],
                                                 logger=self._logger)
                            self.addData(prop_data)
                            try:
                                output = int(p['pin'][4:])
                                self._pinPropData[output] = prop_data
                            except Exception as e:
                                self._logger.error("Failed to parse '{}' output".format(p['pin']))
                                self._logger.debug(e)
                    else:
                        if self.setGpioPinOut(p['pin'], p['initial']):
                            self._propPins[p['pin']] = PropPin(p['pin'], p['variable'], p['initial'], p['alias'])
                            self._logger.info("Pin added from settings : {}".format(p))
                            prop_data = PropData(p['variable'], bool,
                                                 self._gpioLevel(p['initial']),
                                                 alias=p['alias'],
                                                 logger=self._logger)
                            self.addData(prop_data)
                            try:
                                output = int(p['pin'][4:])
                                self._pinPropData[output] = prop_data
                            except Exception as e:
                                self._logger.error("Failed to parse '{}' output".format(p['pin']))
                                self._logger.debug(e)
                else:
                    if p['pin'].startswith('MCP23017'):
                        self._logger.info("Pin ignored from settings : {}".format(p))
                    else:
                        if self.setGpioPinOut(p['pin'], p['initial']):
                            self._propPins[p['pin']] = PropPin(p['pin'], p['variable'], p['initial'], p['alias'])
                            self._logger.info("Pin added from settings : {}".format(p))
                            prop_data = PropData(p['variable'], bool,
                                                 self._gpioLevel(p['initial']),
                                                 alias=p['alias'],
                                                 logger=self._logger)
                            self.addData(prop_data)
                            try:
                                output = int(p['pin'][4:])
                                self._pinPropData[output] = prop_data
                            except Exception as e:
                                self._logger.error("Failed to parse '{}' output".format(p['pin']))
                                self._logger.debug(e)
            except Exception as e:
                self._settings_p.update('ERROR')
                self._logger.warning("Failed add pin from settings : {}".format(p))
                self._logger.warning(e)

    # __________________________________________________________________
    def processSettingsMessage(self, settings):

        try:
            self._settings_p.update('NONE')
            self._settings_date_p.update(NULL_DATE)
            self.sendDataChanges()
            self.cleanupGpioPins()
            json_list = json.loads(settings)
            self.processSettingsJson(json_list)
            with open(SETTINGS_JSON_FILE, 'w', encoding='utf-8') as fp:
                fp.write(settings)
            if self._settings_p.value() == 'ERROR':
                self._settings_p.update('ONLINE ERROR')
            else:
                self._settings_p.update('OK')
            self._settings_date_p.update("%s" % time.ctime(os.path.getmtime(SETTINGS_JSON_FILE)))
            self.sendAllData()
        except json.JSONDecodeError as jex:
            self._logger.error("JSONDecodeError '{}' at {} in : {}".format(jex.msg, jex.pos, jex.doc))
        except Exception as e:
            self._logger.error("Failed to parse JSON settings : {}".format(settings))
            self._logger.debug(e)

    # __________________________________________________________________
    async def readJsonRescue(self, wait):

        await asyncio.sleep(wait)
        if self._settings_date_p.value() == NULL_DATE:
            self._settings_p.update('NONE')
            self._settings_date_p.update(NULL_DATE)
            self.sendDataChanges()
            self.cleanupGpioPins()
            if os.path.isfile(SETTINGS_JSON_FILE):
                try:
                    with open(SETTINGS_JSON_FILE, 'r', encoding='utf-8') as fp:
                        json_list = json.load(fp)
                    self.processSettingsJson(json_list)
                except json.JSONDecodeError as jex:
                    self._logger.error("JSONDecodeError '{}' at {} in: {}".format(jex.msg, jex.pos, jex.doc))
                except Exception as e:
                    self._logger.error("Failed to load JSON file '{0}'".format(self._localFile))
                    self._logger.debug(e)
                if self._settings_p.value() == 'ERROR':
                    self._settings_p.update('OFFLINE ERROR')
                else:
                    self._settings_p.update('OFFLINE')
                self._settings_date_p.update("%s" % time.ctime(os.path.getmtime(SETTINGS_JSON_FILE)))
            self.sendAllData()

    # __________________________________________________________________
    def sendAllData(self):
        super().sendAllData()

    # __________________________________________________________________
    def sendDataChanges(self):
        super().sendDataChanges()

    # __________________________________________________________________
    def setGpioPinOut(self, pin, initial):

        try:
            output = int(pin[4:])
            GPIO.setup(output, GPIO.OUT, initial=self._gpioLevel(initial))
            self._logger.info("GPIO {} set as output (initial={})".format(output, self._gpioLevel(initial)))
        except Exception as e:
            self._logger.error("GPIO setup failed for pin {}".format(pin))
            self._logger.debug(e)
            return False
        return True

    # __________________________________________________________________
    def setMcp23017PinOut(self, pin, initial):

        try:
            self._logger.warning("MCP23017 pin not setup TBD...")
        except Exception as e:
            self._logger.error("MCP23017 setup failed for pin {}".format(pin))
            self._logger.debug(e)
            return False
        return True
