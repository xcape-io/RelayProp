# MegaRelayProp
*Universal Relay Prop for Escape Room with Arduino Mega 2560 connected with Dragino Yún, Ethernet or WiFi shield.*

In your Escape Room, *PiPyRelayProp* centralizes the control of your main relays:
* lights
* electricity
* maglocks (doors)
* smoke machines (warmp-up and shots)

No coding is required, the relay outputs are configured with the [PyRelayControl](https://github.com/xcape-io/RelayProp/tree/master/PyRelayControl) wiring GUI and the commands can be triggered with the [PyRelayControl]([PyRelaySettings](https://github.com/xcape-io/RelayProp/tree/master/PyRelayControl)) panel or a regular [control panel for *Room by xcape.io* users](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#prop-configuration-for-room-by-xcapeio).

<img src="https://github.com/xcape-io/RelayProp/blob/master/docs/megarelayprop.png" width="900">

* [Prepare Arduino IDE and Mega 2560](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#prepare-arduino-ide-and-mega-2560)
* [Installation  for Dragino Yún, Ethernet or WiFi Shield](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#installation-for-dragino-yun-ethernet-or-wifi-shield)
* [Relay Prop settings](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#relay-prop-settings)
* [Relay Prop panel](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#relay-prop-panel)
* [Relay modules](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#relay-modules)
* [Prop commands](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#prop-commands)
* [Prop data messages](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#prop-data-messages)
* [Prop configuration for *Room by xcape.io*](https://github.com/xcape-io/RelayProp/tree/master/MegaRelayProp#prop-configuration-for-room-by-xcapeio)


## Prepare Arduino IDE and Mega 2560
You will find instructions in the <a href="https://github.com/xcape-io/ArduinoProps#1-installation-and-usage" target="_blank">ArduinoProps.md (1. Installation and usage)</a> to install:
* **ArduinoProps** library
* **PubSubClient** library
* **ListLib** library

Then you need to install **ArduinoJson** library:

![](https://github.com/xcape-io/RelayProp/raw/master/docs/images/arduino-install-json.png)

## Installation for Dragino Yún, Ethernet or WiFi Shield
Download <a href="https://github.com/xcape-io/RelayProp/archive/master.zip" target="_blank">`RelayProp-master.zip`</a>, the sketch `MegaRelayProp.ino` is in the **MegaRelayProp** folder in  `RelayProp/MegaRelayProp/`.

Advanced users may clone the <a href="https://github.com/xcape-io/RelayProp" target="_blank">https://github.com/xcape-io/RelayProp</a> repository.

### Arduino Mega 2560 with Dragino Yún Shield
Open the `MegaRelayProp.ino` sketch in the Arduino IDE to set MQTT topics for your Escape Room:
```csharp
MegaRelayProp prop(MegaRelayProp::Bridge,
              u8"Relay Mega", // as MQTT client id, should be unique per client for given broker
              u8"Room/My room/Props/Relay Mega/inbox",
              u8"Room/My room/Props/Relay Mega/outbox",
              u8"Room/My room/Props/Relay Mega/wiring/#",
              "192.168.1.53", // your MQTT server IP address
              1883); // your MQTT server port;
```

Then upload the sktech to the Relay Mega board.

> D0 (RxD) and D1 (TxD) are used by the Arduino Bridge connection, other I/O pins are available.

If **Dragino Yún Shield** has not been setup in Arduino IDE yet, see <a href="https://github.com/xcape-io/ArduinoProps#add-dragino-yun--mega-2560-board-to-arduino-ide-boards-manager" target="_blank">Add Dragino Yún + Mega 2560 board to Arduino IDE boards manager</a> in the README of ArduinoProps library.

#### Dragino Yún shield setup
If you are not familiar with Yún (a Linux SoC bridged to the MCU), you will find help:
* <a href="https://wiki.dragino.com/index.php?title=Yun_Shield" target="_blank">Dragino Yún Shield Wiki</a>
* <a href="https://medium.com/@monajalal/arduino-yun-boad-setup-and-demo-e1161b60e068" target="_blank">Arduino Yún Board Setup and Demo</a> at Medium
* <a href="https://www.arduino.cc/en/Guide/ArduinoYun" target="_blank">Getting Started with the Arduino Yún</a> at arduino.cc
* <a href="https://www.youtube.com/watch?v=9-hPhWHWnvs" target="_blank">Getting Started With Arduino Yú</a>n - Video tutorial on YouTube

### Arduino Mega 2560 with Ethernet Shield
Open the `MegaRelayProp.ino` sketch in the Arduino IDE to set MQTT topics for your Escape Room:

```csharp
MegaRelayProp prop(MegaRelayProp::Ethernet,
              u8"Relay Mega", // as MQTT client id, should be unique per client for given broker
              u8"Room/My room/Props/Relay Mega/inbox",
              u8"Room/My room/Props/Relay Mega/outbox",
              u8"Room/My room/Props/Relay Mega/wiring/#",
              "192.168.1.53", // your MQTT server IP address
              1883); // your MQTT server port;
```

Then upload the sktech to the Relay Mega board.

> All I/O pins are available, the Ethernet shield is connected to Arduino with SPI port.

### Arduino Mega 2560 with WiFi Shield
Open the `MegaRelayProp.ino` sketch in the Arduino IDE to set MQTT topics for your Escape Room:
```csharp
MegaRelayProp prop(MegaRelayProp::WiFi,
              u8"Relay Mega", // as MQTT client id, should be unique per client for given broker
              u8"Room/My room/Props/Relay Mega/inbox",
              u8"Room/My room/Props/Relay Mega/outbox",
              u8"Room/My room/Props/Relay Mega/wiring/#",
              "192.168.1.53", // your MQTT server IP address
              1883); // your MQTT server port;
```

Then upload the sktech to the Relay Mega board.

> All I/O pins are available, the WiFi shield is connected to Arduino with SPI port.


## Relay Prop wiring and control panel
All relay outputs are setup with the *PyRelayControl* GUI:

![](https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/screenshots/pyrelaysettings-main.png)

See [PyRelayControl](https://github.com/xcape-io/RelayProp/tree/master/PyRelayControl)


## Relay modules
See [RELAY_MODULES.md](https://github.com/xcape-io/RelayProp/blob/master/RELAY_MODULES.md)


## Prop commands
Commands are implicitly defined with the *PyRelaySettings* GUI, you can create group commands by naming variables in groups with the `/` separator.

Relay commands are built from the variable name:

* `props:on` : power on the props
* `smoke/on:1` : ower on the smoke machine
* `smoke/fog:1` : release fog from the smoke machine

Group commands uses the `/*` tag: 

* `maglock/*:0` : release all the maglocks
* `door/*:0` : open all the doors


## Prop data messages
Relay state variables are sent as defined with the *PyRelaySettings* GUI, as well as the board and settings informations:

```python
settings:
    0: not configured
    1 to 50: number of pins configured

board:
    Mega: Mega 2560 with Ethernet/WiFi shield
    Mega with bridge: Mega 2560 with Dragino Yún shield: 
```

For example:

```bash
board=Mega with bridge 
settings=9 
```

![Outbox messages](https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/screenshots/outbox-messages.png)


## Prop configuration for *Room by xcape.io*
*Room by xcape.io* users can add the Relay Pi prop to their props:

![Room prop configuration](https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/screenshots/room-prop-settings.png)

And create a regular control panel:

![Room control panel](https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/screenshots/room-prop-control-panel.png)


# MegaRelayEthernetProp alternative
*Relay Prop  on Arduino Mega 2560 + Ethernet Shield.*

<img align="middle" src="https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/warning.png" alt="Warning" /> Not done yet...


# MegaRelayWifiProp alternative
*Relay Prop  on Arduino Mega 2560 + WiFi Shield.*

<img align="middle" src="https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/warning.png" alt="Warning" /> Not done yet...


## Author

**Faure Systems** (Apr 26th, 2020)
* company: FAURE SYSTEMS SAS
* mail: *dev at faure dot systems*
* github: <a href="https://github.com/xcape-io?tab=repositories" target="_blank">xcape-io</a>
* web: <a href="https://xcape.io/" target="_blank">xcape.io</a>