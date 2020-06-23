# PiPyRelayProp
*Relay Prop for Escape Room with Raspberry Pi 3B/3B+/4.*

In your Escape Room, *PiPyRelayProp* centralizes the control of your main relays:
* lights
* electricity
* maglocks (doors)
* smoke machines (warmp-up and shots)

No coding is required, the relay outputs are configured and the commands can be triggered with the [PyRelayControl GUI app]((https://github.com/xcape-io/RelayProp/tree/master/PyRelayControl)).

<img src="https://github.com/xcape-io/RelayProp/blob/master/docs/pipyrelayprop.png" width="900">

* [Prepare your Raspberry Pi as a prop](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#prepare-your-raspberry-pi-as-a-prop)
* [Installation](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#installation)
* [Usage](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#usage)
* [SSH relaunch command](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#ssh-relaunch-command)
* [Relay Prop wiring](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#relay-prop-wiring)
* [Relay Prop panel](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#relay-prop-panel)
* [Relay modules](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#relay-modules)
* [Prop commands](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#prop-commands)
* [Prop data messages](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#prop-data-messages)
* [Prop configuration for *Room by xcape.io*](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#prop-configuration-for-room-by-xcapeio)
* [Add MCP23017 16 pins I/O expander](https://github.com/xcape-io/RelayProp/tree/master/PiPyRelayProp#add-mcp23017-16-pins-io-expander)


## Prepare your Raspberry Pi as a prop
You will find instructions in the <a href="https://github.com/xcape-io/PyProps/blob/master/RASPBERRY_PI_PROPS.md" target="_blank">RASPBERRY_PI_PROPS.md</a>


> A Raspberry Pi prop 16GB Raspbian image from NOOBS 3.3.1 (2020-02-14) is available for download from [PROPS_3_3_1.7z](https://sourceforge.net/projects/xcape/files/Pi%20Prop%20Raspbian%20Images/)
>
> <a href="https://www.7-zip.org/" target="_blank">7Zip</a> is required to unflate .7z the image.


## Installation
Download <a href="https://github.com/xcape-io/RelayProp/archive/master.zip" target="_blank">`RelayProp-master.zip`</a> and copy the ***PiPyControlProp*** folder in  `/home/pi/Room/Props/PiPyRelayProp`.

Advanced users may clone the <a href="https://github.com/xcape-io/RelayProp" target="_blank">https://github.com/xcape-io/RelayProp</a> repository in `/home/pi/Room/Props/RelayProp`.

You can use [PyProps library](https://github.com/xcape-io/PyProps) if you have it installed or the copy of *PyProps core* that is in the folder `./pyprops-core` (see `PYPROPS_CORELIBPATH` in `constants.py`).

Install dependencies
```bash
pip3 install -r requirements.txt
```

Edit `definitions.ini` to set MQTT topics for your prop:
```ini
[mqtt]
; mqtt-sub-* and app-inbox topics are subscribed by MqttConsoleApp
app-inbox = Room/My room/Props/Relay Pi/inbox
app-outbox = Room/My room/Props/Relay Pi/outbox
mqtt-sub-wiring = Room/My room/Props/Relay Pi/wiring

``` 

## Usage
Start `main.py` script in `/home/pi/Room/Props/PiPyRelayProp` with the broker IP address (`-s 192.168.1.42`):

```bash
pi@raspberrypi:~ $ python3 ~/Room/Props/PiPyRelayProp/src/main.py -s 192.168.1.42 -d

Config: {'host': '192.168.1.42'}
INFO - New periodic action added 'send all data' every 30.0 seconds
INFO - New str Publishable 'board' with initial=Pi
INFO - New str Publishable 'wiring' with initial=NONE
INFO - New str Publishable 'wiring-date' with initial=- - -
INFO - New periodic action added 'read JSON rescue' every 3 seconds
INFO - Periodic task created 'send all data' every 30.0 seconds
INFO - Periodic task created 'read JSON rescue' every 3 seconds
WARNING - Program failed to send message (disconnected) : 'DATA board=Pi wiring=NONE wiring-date=- - -'
INFO - Program connected to MQTT server
INFO - Program sending message 'CONNECTED' (mid=1) on Room/My room/Props/Relay Pi/outbox
INFO - Program subscribing to topic (mid=2) : Room/My room/Props/Relay Pi/inbox
INFO - Program subscribing to topic (mid=3) : Room/My room/Props/Relay Pi/wiring
INFO - Program sending message 'DATA board=Pi wiring=NONE wiring-date=- - -' (mid=4) on Room/My room/Props/Relay Pi/outbox
DEBUG - MQTT message is published : mid=1 userdata={'host': '192.168.1.42', 'port': 1883}
INFO - Message published (mid=1)
DEBUG - MQTT topic is subscribed : mid=2 granted_qos=(1,)
INFO - Program susbcribed to topic (mid=2) with QoS (1,)
DEBUG - MQTT topic is subscribed : mid=3 granted_qos=(1,)
INFO - Program susbcribed to topic (mid=3) with QoS (1,)
INFO - Message received : '[{"pin": "GPIO2", "variable": "lights/corridor", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO3", "variable": "lights/lounge", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO4", "variable": "doors/lounge", "initial": 1, "alias": ["locked", "unlocked"]}, {"pin": "GPIO5", "variable": "doors/exit", "initial": 1, "alias": ["locked", "unlocked"]}, {"pin": "GPIO6", "variable": "smoke", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO7", "variable": "drawers/maglock1", "initial": 1, "alias": ["powered", "released"]}, {"pin": "GPIO8", "variable": "drawers/maglock2", "initial": 1, "alias": ["powered", "released"]}, {"pin": "GPIO9", "variable": "drawers/maglock3", "initial": 1, "alias": ["powered", "released"]}]' in Room/My room/Props/Relay Pi/wiring
Room/My room/Props/Relay Pi/wiring [{"pin": "GPIO2", "variable": "lights/corridor", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO3", "variable": "lights/lounge", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO4", "variable": "doors/lounge", "initial": 1, "alias": ["locked", "unlocked"]}, {"pin": "GPIO5", "variable": "doors/exit", "initial": 1, "alias": ["locked", "unlocked"]}, {"pin": "GPIO6", "variable": "smoke", "initial": 0, "alias": ["on", "off"]}, {"pin": "GPIO7", "variable": "drawers/maglock1", "initial": 1, "alias": ["powered", "released"]}, {"pin": "GPIO8", "variable": "drawers/maglock2", "initial": 1, "alias": ["powered", "released"]}, {"pin": "GPIO9", "variable": "drawers/maglock3", "initial": 1, "alias": ["powered", "released"]}]
/home/pi/Room/Props/PiPyRelayProp/src/PiRelayApp.py:307: RuntimeWarning: This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.
  GPIO.setup(output, GPIO.OUT, initial=self._gpioLevel(initial))
INFO - GPIO 2 set as output (initial=0)
INFO - Pin added from wiring : {'pin': 'GPIO2', 'variable': 'lights/corridor', 'initial': 0, 'alias': ['on', 'off']}
INFO - New boolean Publishable 'lights/corridor' (on/off) with initial=0
INFO - GPIO 3 set as output (initial=0)
INFO - Pin added from wiring : {'pin': 'GPIO3', 'variable': 'lights/lounge', 'initial': 0, 'alias': ['on', 'off']}
INFO - New boolean Publishable 'lights/lounge' (on/off) with initial=0
INFO - GPIO 4 set as output (initial=1)
INFO - Pin added from wiring : {'pin': 'GPIO4', 'variable': 'doors/lounge', 'initial': 1, 'alias': ['locked', 'unlocked']}
INFO - New boolean Publishable 'doors/lounge' (locked/unlocked) with initial=1
INFO - GPIO 5 set as output (initial=1)
INFO - Pin added from wiring : {'pin': 'GPIO5', 'variable': 'doors/exit', 'initial': 1, 'alias': ['locked', 'unlocked']}
INFO - New boolean Publishable 'doors/exit' (locked/unlocked) with initial=1
INFO - GPIO 6 set as output (initial=0)
INFO - Pin added from wiring : {'pin': 'GPIO6', 'variable': 'smoke', 'initial': 0, 'alias': ['on', 'off']}
INFO - New boolean Publishable 'smoke' (on/off) with initial=0
INFO - GPIO 7 set as output (initial=1)
INFO - Pin added from wiring : {'pin': 'GPIO7', 'variable': 'drawers/maglock1', 'initial': 1, 'alias': ['powered', 'released']}
INFO - New boolean Publishable 'drawers/maglock1' (powered/released) with initial=1
INFO - GPIO 8 set as output (initial=1)
INFO - Pin added from wiring : {'pin': 'GPIO8', 'variable': 'drawers/maglock2', 'initial': 1, 'alias': ['powered', 'released']}
INFO - New boolean Publishable 'drawers/maglock2' (powered/released) with initial=1
INFO - GPIO 9 set as output (initial=1)
INFO - Pin added from wiring : {'pin': 'GPIO9', 'variable': 'drawers/maglock3', 'initial': 1, 'alias': ['powered', 'released']}
INFO - New boolean Publishable 'drawers/maglock3' (powered/released) with initial=1
INFO - Program sending message 'DATA board=Pi wiring=OK wiring-date=Sat May  9 10:10:22 2020 lights/corridor=off lights/lounge=off doors/lounge=locked doors/exit=locked smoke=off drawers/maglock1=powered drawers/maglock2=powered drawers/maglock3=powered' (mid=5) on Room/My room/Props/Relay Pi/outbox
DEBUG - MQTT message is published : mid=4 userdata={'host': '192.168.1.42', 'port': 1883}
INFO - Message published (mid=4)
INFO - Message received : '@PING' in Room/My room/Props/Relay Pi/inbox
INFO - Program sending message 'PONG' (mid=6) on Room/My room/Props/Relay Pi/outbox
DEBUG - MQTT message is published : mid=5 userdata={'host': '192.168.1.42', 'port': 1883}
INFO - Message published (mid=5)
DEBUG - MQTT message is published : mid=6 userdata={'host': '192.168.1.42', 'port': 1883}
INFO - Message published (mid=6)
```


## SSH relaunch command
The command to relaunch the prop is :

```bash
$ ps aux | grep python | grep -v "grep python" | grep PiPyRelayProp/src/main.py | awk '{print $2}' | xargs kill -9 && screen -d -m python3 /home/pi/Room/Props/PiPyRelayProp/src/main.py -s %BROKER%

```


## Relay Prop wiring and control panel
All relay outputs are setup with the *PyRelayControl* GUI:

![](https://github.com/xcape-io/RelayProp/blob/master/docs/screenshots/pyrelaywiring-main.png)


See [PyRelayControl](https://github.com/xcape-io/RelayProp/tree/master/PyRelayControl)


## Relay modules
See [RELAY_MODULES.md](https://github.com/xcape-io/RelayProp/blob/master/RELAY_MODULES.md)


## Prop commands
Commands are implicitly defined with the *wiring* GUI, you can create group commands by naming variables in groups with the `/` separator.

Relay commands are built from the variable name:

* `lights/corridor:1` : switch on the light in the corridor
* `drawers/maglock2:0` : release the *maglock2* of drawers

Group commands uses the `/*` tag: 

* `lights/*:0` : switch off all the lights
* `drawers/*:1` : power on all the maglocks of drawers

You can create command aliases for a better `DATA` messages reading or for translation.

Aliases are defined in `constants.py`:

```python
COMMANDS_SYNONYMS_HIGH = ['on', 'close']
COMMANDS_SYNONYMS_LOW = ['off', 'open']
```


## Prop data messages
Relay state variables are sent as defined with the *wiring* GUI, as well as the board and wiring informations:

```python
wiring:
    NONE: not loaded
    OFFLINE ERROR: error while loading offline wiring
    OFFLINE: loaded from local file
    ONLINE ERROR: error while loading online wiring
    OK: loaded from MQTT broker

board:
    Pi: bare Raspberry Pi
    Pi MCP23017: Raspberry Pi with MCP23017 expander
```

For example:

```bash
board=Pi 
wiring=OK 
wiring-date=Sat May  9 10:10:22 2020
```

![Outbox messages](https://github.com/xcape-io/RelayProp/blob/master/PiPyRelayProp/screenshots/outbox-messages.png)


## Prop configuration for *Room by xcape.io*
*Room by xcape.io* users can add the Relay Pi prop to their props:

![Room prop configuration](https://github.com/xcape-io/RelayProp/blob/master/PiPyRelayProp/screenshots/room-prop-wiring.png)

And create a regular control panel:

![Room control panel](https://github.com/xcape-io/RelayProp/blob/master/PiPyRelayProp/screenshots/room-prop-control-panel.png)


## Add MCP23017 16 pins I/O expander

<img align="middle" src="https://github.com/xcape-io/RelayProp/blob/master/PiPyRelayProp/warning.png" alt="Warning" /> Not done yet...


## Author

**Faure Systems** (Apr 26th, 2020)
* company: FAURE SYSTEMS SAS
* mail: *dev at faure dot systems*
* github: <a href="https://github.com/xcape-io?tab=repositories" target="_blank">xcape-io</a>
* web: <a href="https://xcape.io/" target="_blank">xcape.io</a>