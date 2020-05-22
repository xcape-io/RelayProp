# PyRelaySettings
*<a href="https://www.learnpyqt.com/" target="_blank">PyQt5</a> applet to configure a Relay Prop.*
 
* [Installation](https://github.com/xcape-io/RelayProp/tree/master/PyRelaySettings#installation)
* [Usage](https://github.com/xcape-io/RelayProp/tree/master/PyRelaySettings#usage)

## Installation

### Installation on Windows

1. First install Python 3.8.x in `C:\Python38` ([Windows x86-64 executable installer](https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe) from <a href="https://www.python.org/downloads/release/python-382/" target="_blank">python.org</a>)

2. Download [`RelaySettingsInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelaySettings/RelaySettingsInstallation.zip) from this GitHub repository 

3. Unflate it in a folder of your choice (for *<a href="https://xcape.io/" target="_blank">xcape.io</a> Room* users, choose the **Plugins** folder).

4. Run `install.bat` with a double-click to create the Python virtual environment (*venv*).

5. Run `run.bat` to start the Relay Prop settings app.

See [Usage](https://github.com/xcape-io/RelayProp/tree/master/PyRelaySettings#usage).

### Installation on Debian based Linux distros
*PyRelaySettings* is a pure python applet so you can install it on any computer running python with <a href="https://www.learnpyqt.com/" target="_blank">PyQt5</a>.

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

1. Download [`RelaySettingsInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelaySettings/RelaySettingsInstallation.zip) from this GitHub repository 

2. Unflate it in a folder of your choice

3. From this folder, install requirements
    ```bash
    $ pip3 install -r requirements.txt
    ```

4. Start the settings app, assuming your MQTT broker IP address is 192.168.1.42
    ```bash
    $ python3 main.py -s 192.168.1.42
    ```

See [Usage](https://github.com/xcape-io/RelayProp/tree/master/PyRelaySettings#usage).

### Installation on Raspberry Pi (Raspbian)
With the new Raspberry Pi 4 with 2 HDMI outputs and 4GB memory, controlling your escape room with a Raspberry Pi starts to make sense.

You will have to install following Python packages:
```bash
$ sudo apt-get update
$ sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
$ sudo apt-get install python3-pyqt5 python3-pyqt5-dbg
```

Then:

1. Download [`RelaySettingsInstallation.zip`](https://github.com/xcape-io/RelayProp/raw/master/PyRelaySettings/RelaySettingsInstallation.zip) from this GitHub repository 

2. Unflate it in a folder of your choice

3. From this folder, install requirements
    ```bash
    $ pip3 install -r requirements.txt
    ```

4. Start the settings app, assuming your MQTT broker IP address is 192.168.1.42
    ```bash
    $ python3 main.py -s 192.168.1.42
    ```

See [Usage](https://github.com/xcape-io/RelayProp/tree/master/PyRelaySettings#usage).

### Installation on Mac

PyQt5 installation on Mac can be tricky, see <a href="https://www.learnpyqt.com/installation/installation-mac/" target="_blank">PyQt5 installation on Mac at LearnPyQt</a>.


## Usage
![](https://github.com/xcape-io/relayprop/blob/master/docs/screenshots/pyrelayrettings-main.png)

Click on a pin button to configure:

![](https://github.com/xcape-io/relayprop/blob/master/docs/screenshots/pyrelayrettings-pin.png)

> To move a configuration to another pin, select an available pin in the output field.

To configure the relay prop, click the configure button (in main dialog top right):

![](https://github.com/xcape-io/relayprop/blob/master/docs/screenshots/pyrelayrettings-prop.png)


## Author

**Marie FAURE** (Apr 26th, 2020)
* company: FAURE SYSTEMS SAS
* mail: *dev at faure dot systems*
* github: <a href="https://github.com/fauresystems?tab=repositories" target="_blank">fauresystems</a>
* web: <a href="https://faure.systems/" target="_blank">Faure Systems</a>