#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
constants.py

Contains all the application constants. As a rule all constants are named in all caps.
'''

APPLICATION = "PiPyRelayProp"

PYPROPS_CORELIBPATH = './pyprops-core'

PUBLISHALLDATA_PERIOD = 30.0

USE_GPIO = True

#__________________________________________________________________
# Required by MqttApp
CONFIG_FILE = '.config.yml'

MQTT_DEFAULT_HOST = 'localhost'
MQTT_DEFAULT_PORT = 1883
MQTT_DEFAULT_QoS = 1

MQTT_KEEPALIVE = 15 # 15 seconds is default MQTT_KEEPALIVE in Arduino PubSubClient.h

#__________________________________________________________________
# Required by PiPyRelayProp
import os
if USE_GPIO and os.path.isfile('/opt/vc/include/bcm_host.h'):
	import RPi.GPIO as GPIO

#   Addr(BIN)      Addr(hex)
#XXX X  A2 A1 A0
#010 0  1  1  1      0x27
#010 0  1  1  0      0x26
#010 0  1  0  1      0x25
#010 0  1  0  0      0x24
#010 0  0  1  1      0x23
#010 0  0  1  0      0x22
#010 0  0  0  1      0x21
#010 0  0  0  0      0x20

#MCP23017_ADDRESS = 0x27

BOARD_PI = 'Pi'
BOARD_PI_MCP23017 = 'Pi MCP23017'
GPIO_CLEANUP = False  # if board is used exclusively as Relay Prop
GPIO_LOW = 0
GPIO_HIGH = 1
NULL_DATE = '- - -'

SETTINGS_JSON_FILE = './settings.json'

COMMANDS_SYNONYMS_HIGH = ['on', 'close']
COMMANDS_SYNONYMS_LOW = ['off', 'open']
