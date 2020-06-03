
# PyRelayControl
*<a href="https://www.learnpyqt.com/" target="_blank">PyQt5</a> relay control applet.*

<img align="middle" src="https://github.com/xcape-io/RelayProp/blob/master/MegaRelayProp/warning.png" alt="Warning" /> Early development stage. A lot of changes to come yet...

 
## Installation

### Installation on Windows

1. First install Python 3.8.x in `C:\Python38` ([Windows x86-64 executable installer](https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe) from <a href="https://www.python.org/downloads/release/python-382/" target="_blank">python.org</a>)

2. Download [`RelayControlInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelayControl/RelayControlInstallation.zip) from this GitHub repository 

3. Unflate it in a folder of your choice (for *<a href="https://xcape.io/" target="_blank">xcape.io</a> Room* users, choose the **Plugins** folder).

4. Run `install.bat` with a double-click to create the Python virtual environment (*venv*).

5. Set MQTT broker IP address in `constants.py`

    ```python
    MQTT_DEFAULT_HOST = 'localhost'  # replace localhost with your broker IP address
    ```

6. Run `test.bat` to test your new settings app.

### Installation on Debian based Linux distros
*PyRelayControl* is a pure python applet so you can install it on any computer running python with <a href="https://www.learnpyqt.com/" target="_blank">PyQt5</a>.

#### Example of installation on Ubuntu/Debian based distros
You will have to install following Python packages:
```bash
$ sudo apt-get update
$ sudo apt-get install python3-pip
$ pip3 install --user pyqt5
$ sudo apt-get install python3-pyqt5
$ sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
```

Then:

1. Download [`RelayControlInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelayControl/RelayControlInstallation.zip) from this GitHub repository 

2. Unflate it in a folder of your choice

3. From this folder, install requirements
    ```bash
    $ pip3 install -r requirements.txt
    ```

4. Start the settings app, assuming your MQTT broker IP address is 192.168.1.42
    ```bash
    $ python3 main.py -s 192.168.1.42
    ```

### Installation on Raspberry Pi (Raspbian)
With the new Raspberry Pi 4 with 2 HDMI outputs and 4GB memory, controlling your escape room with a Raspberry Pi starts to make sense.

You will have to install following Python packages:
```bash
$ sudo apt-get update
$ sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
$ sudo apt-get install python3-pyqt5 python3-pyqt5-dbg
```

Then:

1. Download [`RelayControlInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelayControl/RelayControlInstallation.zip) from this GitHub repository 

2. Unflate it in a folder of your choice

3. From this folder, install requirements
    ```bash
    $ pip3 install -r requirements.txt
    ```

4. Start the settings app, assuming your MQTT broker IP address is 192.168.1.42
    ```bash
    $ python3 main.py -s 192.168.1.42
    ```

### Installation on Mac

PyQt5 installation on Mac can be tricky, see <a href="https://www.learnpyqt.com/installation/installation-mac/" target="_blank">PyQt5 installation on Mac at LearnPyQt</a>.


## Usage
At fisrt start, configure the relay prop:

![](https://github.com/xcape-io/RelayProp/blob/master/docs/screenshots/configure-control.png?raw=true)

To configure the relay prop:

1. Choose Arduino or Raspberry board model
2. Set board option if any
3. Edit props MQTT topic
4. Set MQTT broker IP address and port 

At first start, when choosing board model:

* prop name is filled with a default name
* inbox is filled with *xcape.io* recommandation
* outbox is filled as well
* settings is filled too


## Wiring settings
![](https://github.com/xcape-io/RelayProp/blob/master/docs/screenshots/pyrelaysettings-main.png?raw=true)

Click on a pin button to configure:

![](https://github.com/xcape-io/RelayProp/blob/master/docs/screenshots/pyrelaysettings-pin.png?raw=true)

> To move a configuration to another pin, select an available pin in the output field.

To configure the relay prop, click the configure button (in main dialog top right):

![](https://github.com/xcape-io/relayprop/blob/master/docs/screenshots/pyrelaysettings-prop.png?raw=true)


## Author

**Marie FAURE** (May 13th, 2020)
* company: FAURE SYSTEMS SAS
* mail: *dev at faure dot systems*
* github: <a href="https://github.com/fauresystems?tab=repositories" target="_blank">fauresystems</a>
* web: <a href="https://faure.systems/" target="_blank">Faure Systems</a>