#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applet.py
MIT License (c) Marie Faure <dev at faure dot systems>

Applet application extends MqttApplet.
"""

from constants import *
from MqttApplet import MqttApplet
from MainDialog import MainDialog
from PropSettingsDialog import PropSettingsDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import os, sys
import codecs
import configparser

try:
    MQTT_KEEPALIVE
except NameError:
    MQTT_KEEPALIVE = 15


class Applet(MqttApplet):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self.setApplicationDisplayName(APPDISPLAYNAME)

        self._propSettings = configparser.ConfigParser()
        prop_ini = 'prop.ini'
        if os.path.isfile(prop_ini):
            self._propSettings.read_file(codecs.open(prop_ini, 'r', 'utf8'))

        if 'prop' not in self._propSettings.sections():
            self._propSettings.add_section('prop')

        if 'board' not in self._propSettings['prop']:
            dlg = PropSettingsDialog(self._propSettings, self._logger)
            dlg.setModal(True)
            dlg.exec()

            with open('prop.ini', 'w') as configfile:
                self._propSettings.write(configfile)

        if 'board' not in self._propSettings['prop']:
            self._logger.info(self.tr("Relay prop board is not configured"))
            # no event loop to quit
            sys.exit()

        if 'broker_address' in self._propSettings['prop']:
            self._mqttServerHost = self._propSettings['prop']['broker_address']

        if 'broker_port' in self._propSettings['prop']:
            self._mqttServerPort = int(self._propSettings['prop']['broker_port'])

        if 'prop_outbox' in self._propSettings['prop']:
            self._mqttSubscriptions.append(self._propSettings['prop']['prop_outbox'])

        self._MainDialog = MainDialog(self.tr("Relay Settings"), './x-settings.png',
                                        self._propSettings,
                                        self._logger)
        self._MainDialog.aboutToClose.connect(self.exitOnClose)
        self._MainDialog.publishMessage.connect(self.publishMessage)
        self._MainDialog.publishRetainedMessage.connect(self.onPublishRetainedMessage)
        self._MainDialog.resetBrokerConnection.connect(self.onResetBrokerConnection)

        self.connectedToMqttBroker.connect(self._MainDialog.onConnectedToMqttBroker)
        self.disconnectedToMqttBroker.connect(self._MainDialog.onDisconnectedToMqttBroker)
        self.messageReceived.connect(self._MainDialog.onMessageReceived)

        self._MainDialog.show()

    # __________________________________________________________________
    @pyqtSlot()
    def exitOnClose(self):
        self._logger.info(self.tr("exitOnClose"))
        self.quit()

    # __________________________________________________________________
    @pyqtSlot(str, str)
    def onPublishRetainedMessage(self, topic, message):

        if self._mqttConnected:
            try:
                (result, mid) = self._mqttClient.publish(topic, message, qos=MQTT_DEFAULT_QoS, retain=True)
                self._logger.info(
                    "{0} '{1}' (mid={2}) on {3}".format(self.tr("Program sending message"), message, mid, topic))
            except Exception as e:
                self._logger.error(
                    "{0} '{1}' on {2}".format(self.tr("MQTT API : failed to call publish() for"), message, topic))
                self._logger.debug(e)
        else:
            self._logger.info("{0} : '{1}'".format(self.tr("Program failed to send message (disconnected)"), message))

    # __________________________________________________________________
    @pyqtSlot()
    def onResetBrokerConnection(self):

        self._mqttSubscriptions = []
        if 'prop_outbox' in self._propSettings['prop']:
            self._mqttSubscriptions.append(self._propSettings['prop']['prop_outbox'])

        broker_changed = False
        if 'broker_address' in self._propSettings['prop']:
            if self._mqttServerHost != self._propSettings['prop']['broker_address']:
                self._mqttServerHost = self._propSettings['prop']['broker_address']
                broker_changed = True
        broker_port = self._propSettings['prop']['broker_port']
        if broker_port.isdigit() and self._mqttServerPort != int(broker_port):
            self._mqttServerPort = int(broker_port)
            broker_changed = True

        if broker_changed or not self._mqttConnected:
            try:
                self._mqttClient.connect_async(self._mqttServerHost, port=self._mqttServerPort, keepalive=MQTT_KEEPALIVE)
                self._logger.info(
                    self.tr("Program initiated asynchronous connection to ") + self._mqttServerHost + ":" + str(
                        self._mqttServerPort))
            except Exception as e:
                self._logger.error(self.tr("MQTT API : failed to call connect_async()"))
                self._logger.debug(e)
        else:
            self._mqttClient.reconnect()

