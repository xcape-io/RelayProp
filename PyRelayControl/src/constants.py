#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
constants.py

Contains all the control applet constants.
"""

# __________________________________________________________________
# Required by MqttApplet
ORGANIZATIONDOMAIN = "xcape.io"
ORGANIZATIONNAME = "xcape.io"

CONFIG_FILE = '.config.yml'

APPLICATION = "Relay Prop"

PYPROPS_CORELIBPATH = '../core' # however ./core is preferred if present

MQTT_DEFAULT_HOST = 'localhost'  # replace localhost with your broker IP address
MQTT_DEFAULT_PORT = 1883
MQTT_DEFAULT_QoS = 1

# __________________________________________________________________
# Required by RelayApplet
APPDISPLAYNAME = APPLICATION

# __________________________________________________________________
# Required by the widgets
LAYOUT_FILE = '.layout.yml'
WIRING_LAYOUT_FILE = '.wiring_layout.yml'

# __________________________________________________________________
# Required by the application
DATALED_IMAGE_ON = './images/led-circle-yellow.svg'
DATALED_IMAGE_OFF = './images/led-circle-generic.svg'

GPIO_LOW = 0
GPIO_HIGH = 1

MEGA_YUN_ONLY = True
PI_MPC23017_NOT_SUPPORTED = True

LOCAL_ARDUINO_MEGA2560_JSON = 'arduino_mega2560.json'
LOCAL_ARDUINO_MEGA2560_BRIDGE_JSON = 'arduino_mega2560_bridge.json'
LOCAL_STM32_NUCLEO144_JSON = 'stm32_nucleo144.json'
LOCAL_PI_JSON = 'raspberry_pi.json'
LOCAL_PI_MCP23017_JSON = 'raspberry_pi_23017.json'

ALIAS_INPUT_WIDTH = 70
VARIABLE_INPUT_WIDTH = 110

MEGA_ALIAS_MAX_LENGTH = 6      # these maximums are used in MegaCentralProp.cpp
MEGA_VARIABLE_MAX_LENGTH = 12  # some utf8 chars take more than 1 byte
MEGA_TOTAL_MAX_LENGTH = 14

SWITCH_IMAGES = {}
SWITCH_IMAGES['default'] = ('./images/led-circle-yellow.svg', './images/led-circle-generic.svg')
SWITCH_IMAGES['door'] = ('./images/door-closed.svg', './images/door-opened.svg')
SWITCH_IMAGES['smoke'] = ('./images/smoke_on.svg', './images/smoke_off.svg')
SWITCH_IMAGES['plug'] = ('./images/plug.svg', './images/unplugged.svg')
SWITCH_IMAGES['relay'] = ('./images/relay_closed.svg', './images/relay_opened.svg')


HTML = '''
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>Relay Prop Pinout</title>
<style>
body {
font-family: Helvetica, Arial;	
font-size: 10px;
}

h1 {
font-size: 14px;	
font-weight: normal;	
color: #333333;	
}

th {
padding: 8px;
}

td {
text-align: center;
}

td {
text-align: center;
}
</style>
</head>

<body>
{{BODY}}
</body>
</html>
'''
TITLE = '''
<h1 style="text-align:center">Prop: {{PROP}}</h1>
<p style="text-align:center; font-size:12px">{{FILE}}</p>
<p></p>
'''
TABLE = '''
<table cellpadding="2">
<tr>
<th>Output</th>
<th>Variable</th>
<th>Initial</th>
<th>HIGH</th>
<th>LOW</th>
</tr>
{{ROWS}}
</table>        
'''
ROW = '''
<tr>
<td style="text-align:left">{{OUTPUT}}</td>
<td>{{VARIABLE}}</td>
<td>{{INITIAL}}</td>
<td>{{HIGH}}</td>
<td>{{LOW}}</td>
</tr>
'''
