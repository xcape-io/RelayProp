#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiringDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to edit Relay prop wiring.

Starting with Python 3.7, the regular dict became order preserving,
so it is no longer necessary to specify collections.OrderedDict for
JSON generation and parsing.
"""

import json
import os
import re
import yaml

from collections import OrderedDict  # remember the order entries are added

from constants import *
from AppletDialog import AppletDialog
from LedWidget import LedWidget
from PropPin import PropPin
from PropPinDialog import PropPinDialog

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QPushButton, QLabel, QDialog, QWidget
from PyQt5.QtWidgets import QSizePolicy, QScrollArea, QMessageBox


class WiringDialog(AppletDialog):
    propDataReveived = pyqtSignal(dict)
    publishMessage = pyqtSignal(str, str)
    publishRetainedMessage = pyqtSignal(str, str)
    reloadPropPinsDisplay = pyqtSignal()
    switchLed = pyqtSignal(str, str)

    # __________________________________________________________________
    def __init__(self, title, icon, prop_settings, layout_file, logger):

        # members required by _buildUi() must be set before calling super().__init__()
        self._logger = logger
        self._localFile = ''
        self._propSettings = prop_settings
        self._propPins = {}

        self._boardMegaPins = []
        self._boardMegaWithBridgePins = []
        for digital in range(50):
            if digital == 0:
                self._boardMegaPins.append(("D{} (RxD)".format(digital), "D{}".format(digital)))
            elif digital == 1:
                self._boardMegaPins.append(("D{} (TxD)".format(digital), "D{}".format(digital)))
            elif digital >= 2 and digital <= 13:
                self._boardMegaPins.append(("D{} (PWM)".format(digital), "D{}".format(digital)))
                self._boardMegaWithBridgePins.append(("D{} (PWM)".format(digital), "D{}".format(digital)))
            else:
                self._boardMegaPins.append(("D{}".format(digital), "D{}".format(digital)))
                self._boardMegaWithBridgePins.append(("D{}".format(digital), "D{}".format(digital)))
        print("Mega", len(self._boardMegaPins), "pins", self._boardMegaPins)
        print("Mega with bridge", len(self._boardMegaWithBridgePins), "pins", self._boardMegaWithBridgePins)

        self._boardPiPins = []
        self._boardPiWithExpanderPins = []
        for gpio in range(2, 26 + 1):
            if gpio == 2:
                self._boardPiPins.append((("GPIO{} (SDA)".format(gpio), "GPIO{}".format(gpio))))
            elif gpio == 3:
                self._boardPiPins.append((("GPIO{} (SCL)".format(gpio), "GPIO{}".format(gpio))))
            else:
                self._boardPiPins.append((("GPIO{}".format(gpio), "GPIO{}".format(gpio))))
                self._boardPiWithExpanderPins.append((("GPIO{}".format(gpio), "GPIO{}".format(gpio))))
        for i in range(8):
            self._boardPiWithExpanderPins.append((("MCP23017_GPIOA{}".format(i), "MCP23017_GPIOA{}".format(i))))
        for i in range(8):
            self._boardPiWithExpanderPins.append((("MCP23017_GPIOB{}".format(i), "MCP23017_GPIOB{}".format(i))))
        print("Pi", len(self._boardPiPins), "pins", self._boardPiPins)
        print("Pi with MCP23017", len(self._boardPiWithExpanderPins), "pins", self._boardPiWithExpanderPins)

        if self._propSettings['prop']['board'] == 'mega':
            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                self._boardPins = self._boardMegaWithBridgePins
                self._localFile = LOCAL_ARDUINO_MEGA2560_BRIDGE_JSON
            else:
                self._boardPins = self._boardMegaPins
                self._localFile = LOCAL_ARDUINO_MEGA2560_JSON
        else:
            if 'pi_expander' in self._propSettings['prop'] and self._propSettings['prop']['pi_expander'] == '1':
                self._boardPins = self._boardPiWithExpanderPins
                self._localFile = LOCAL_PI_MCP23017_JSON
            else:
                self._boardPins = self._boardPiPins
                self._localFile = LOCAL_PI_JSON

        super().__init__(title, icon, layout_file, logger)

        self._reDataSplitValues = re.compile(r'[^\s]+\s*=')
        self._reDataVariables = re.compile(r'([^\s]+)\s*=')

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))

        self.setMinimumWidth(450)
        self.setMinimumHeight(410)

        self.setVisible(not os.path.exists(self._localFile))

        self._readJson()
        self.reloadPropPinsDisplay.emit()

    # __________________________________________________________________
    def _buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        if 'prop_name' in self._propSettings['prop']:
            prop_name = self._propSettings['prop']['prop_name']
        else:
            prop_name = 'Prop'

        self._led = LedWidget(prop_name, QSize(40, 20))
        self._led.setRedAsBold(False)
        self._led.setRedAsRed(True)
        self._led.switchOn('red', self.tr("MQTT broker not connected"))

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._led)
        main_layout.addLayout(header_layout)

        self._pinsDisplayWidget = QWidget()
        self._pinsGridLayout = QGridLayout(self._pinsDisplayWidget)

        scrollArea = QScrollArea()
        scrollArea.setObjectName('ScrollingArea')
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self._pinsDisplayWidget)
        scrollArea.setStyleSheet("#ScrollingArea { border: 1px solid #CCCCCC }")
        main_layout.addWidget(scrollArea)

        self._localFileDisplay = QLabel(self._localFile)

        upload_button = QPushButton(" {} ".format(self.tr(" Upload wiring to broker ")))
        upload_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        upload_button.setFocusPolicy(Qt.NoFocus)

        clear_button = QPushButton(self.tr("Clear"))
        clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        clear_button.setFocusPolicy(Qt.NoFocus)

        print_button = QPushButton(self.tr("Print"))
        print_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        print_button.setFocusPolicy(Qt.NoFocus)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        button_layout.addWidget(upload_button)
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        button_layout.addWidget(print_button)
        main_layout.addLayout(button_layout)

        self._brokerTopicDisplay = QLabel(self._localFile)
        if 'prop_wiring' in self._propSettings['prop']:
            self._brokerTopicDisplay.setText(self._propSettings['prop']['prop_wiring'])

        broker_layout = QHBoxLayout()
        broker_layout.setSpacing(4)
        broker_layout.addWidget(QLabel(self.tr("Broker topic:")))
        broker_layout.addWidget(self._brokerTopicDisplay)
        broker_layout.addStretch()
        main_layout.addLayout(broker_layout)

        close_button = QPushButton(self.tr("Close"))
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        close_button.setFocusPolicy(Qt.NoFocus)

        close_layout = QHBoxLayout()
        close_layout.addWidget(QLabel(self.tr("Local file:")))
        close_layout.addWidget(self._localFileDisplay)
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)

        self.setLayout(main_layout)

        self.switchLed.connect(self._led.switchOn)
        self.reloadPropPinsDisplay.connect(self.onReloadPropPinsDisplay)
        clear_button.released.connect(self.clear)
        print_button.released.connect(self.print)
        close_button.released.connect(self.accept)
        upload_button.released.connect(self.upload)

    # __________________________________________________________________
    def _parsePropData(self, message):

        variables = {}
        data = message[5:]
        vars = re.split(self._reDataSplitValues, data)[1:]

        try:
            m = re.findall(self._reDataVariables, data)
            if m:
                i = 0
                for var in m:
                    variables[var] = vars[i].strip()
                    i = i + 1
        except Exception as e:
            self._logger.debug(e)

        self.propDataReveived.emit(variables)

    # __________________________________________________________________
    def _readJson(self):

        self._propPins = {}
        if os.path.isfile(self._localFile):
            try:
                with open(self._localFile, 'r', encoding='utf-8') as fp:
                    json_list = json.load(fp)
                for p in json_list:
                    try:
                        key = self.pinToKey(p['pin'])
                        if key is not None:
                            self._propPins[key] = PropPin(key, p['variable'], p['initial'], p['alias'])
                            self._logger.info("Pin added from settings : {}".format(p))
                    except Exception as e:
                        self._logger.warning("Failed add pin from settings : {}".format(p))
                        self._logger.warning(e)
            except json.JSONDecodeError as jex:
                self._logger.error("JSONDecodeError '{}' at {} in: {}".format(jex.msg, jex.pos, jex.doc))
            except Exception as e:
                self._logger.error("Failed to load JSON file '{0}'".format(self._localFile))
                self._logger.debug(e)

    # __________________________________________________________________
    def _saveJson(self):

        pin_list = []
        for key, pin in self._boardPins:
            if key in self._propPins:
                pin_dict = {}
                pin_dict['pin'] = pin
                pin_dict['variable'] = self._propPins[key]._variable
                pin_dict['initial'] = self._propPins[key]._initial
                pin_dict['alias'] = self._propPins[key]._alias
                pin_list.append(pin_dict)

        with open(self._localFile, 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(pin_list, indent=2, ensure_ascii=False))  # for UTF-8 encoding

    # __________________________________________________________________
    @pyqtSlot()
    def clear(self):

        msg = QMessageBox()
        msg.setWindowIcon(self.windowIcon())
        msg.setIcon(QMessageBox.Question)
        msg.setText(self.tr("Delete the whole configuration?"))
        msg.setWindowTitle("Confirm deletion")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        if msg.exec_() == QMessageBox.Yes:
            self._propPins = {}
            self._saveJson()
            self.reloadPropPinsDisplay.emit()

    # __________________________________________________________________
    def closeEvent(self, e):

        pass  # avboid base class event

    # __________________________________________________________________
    @pyqtSlot()
    def layoutLoadSettings(self):

        if os.path.isfile(WIRING_LAYOUT_FILE):
            with open(WIRING_LAYOUT_FILE, 'r') as layoutfile:
                layout = yaml.load(layoutfile, Loader=yaml.SafeLoader)

            self.move(QPoint(layout['x'], layout['y']))
            self.resize(QSize(layout['w'], layout['h']))

    # __________________________________________________________________
    @pyqtSlot()
    def onConnectedToMqttBroker(self):

        if self._led.color() == 'red':
            if 'prop_name' in self._propSettings['prop']:
                self._led.switchOn('yellow', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                               self.tr("connected")))
            else:
                self._led.switchOn('yellow')

    # __________________________________________________________________
    @pyqtSlot()
    def onDisconnectedToMqttBroker(self):

        if 'prop_name' in self._propSettings['prop']:
            self._led.switchOn('red', self.tr("MQTT broker not connected"))
        else:
            self._led.switchOn('red')

    # __________________________________________________________________
    @pyqtSlot(str, str)
    def onMessageReceived(self, topic, message):

        if message.startswith("DISCONNECTED"):
            if 'prop_name' in self._propSettings['prop']:
                self._led.switchOn('red', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                               self.tr("disconnected")))
            else:
                self._led.switchOn('red')
        else:
            if self._led.color() != 'green':
                if 'prop_name' in self._propSettings['prop']:
                    self._led.switchOn('green', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                                  self.tr("connected")))
                else:
                    self._led.switchOn('green')

        if 'prop_outbox' in self._propSettings['prop']:
            if topic == self._propSettings['prop']['prop_outbox'] and message.startswith('DATA '):
                self._parsePropData(message)

    # __________________________________________________________________
    @pyqtSlot()
    def onPinConfiguration(self):

        s = self.sender()
        pin_key = s.text().strip()

        if pin_key in self._propPins:
            pin = self._propPins[pin_key]
        else:
            pin = PropPin()  # null pin

        pins_available = []
        for p, _ in self._boardPins:
            if p == pin_key:
                pins_available.append(p)
            else:
                if p not in self._propPins:
                    pins_available.append(p)

        mega = (self._propSettings['prop']['board'] == 'mega')

        dlg = PropPinDialog(pin_key, pin, pins_available, self._propPins, mega)
        dlg.setModal(True)
        dlg.move(self.pos() + QPoint(130, 100))
        ret = dlg.exec()
        if ret == QDialog.Accepted:
            if pin is not None:
                self._propPins[pin.getPin()] = pin
        elif ret == -1:
            pin_to_remove = pin.getPin()
            if pin_to_remove in self._propPins:
                msg = QMessageBox()
                msg.setWindowIcon(self.windowIcon())
                msg.setIcon(QMessageBox.Question)
                msg.setText(self.tr("Delete {} configuration?".format(pin_to_remove)))
                msg.setWindowTitle("Confirm deletion")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                if msg.exec_() == QMessageBox.Yes:
                    self._propPins.pop(pin_to_remove)

        self._saveJson()
        self.reloadPropPinsDisplay.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onPropChanged(self):

        if 'prop_name' in self._propSettings['prop']:
            self._led.updateDefaultText(self._propSettings['prop']['prop_name'])

        if self._propSettings['prop']['board'] == 'mega':
            self._boardPins = self._boardMegaPins
            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                self._boardPins = self._boardMegaWithBridgePins
                self._localFile = LOCAL_ARDUINO_MEGA2560_BRIDGE_JSON
            else:
                self._boardPins = self._boardMegaPins
                self._localFile = LOCAL_ARDUINO_MEGA2560_JSON
        else:
            if 'pi_expander' in self._propSettings['prop'] and self._propSettings['prop']['pi_expander'] == '1':
                self._boardPins = self._boardPiWithExpanderPins
                self._localFile = LOCAL_PI_MCP23017_JSON
            else:
                self._boardPins = self._boardPiPins
                self._localFile = LOCAL_PI_JSON

        self._localFileDisplay.setText(self._localFile)

        if 'prop_wiring' in self._propSettings['prop']:
            self._brokerTopicDisplay.setText(self._propSettings['prop']['prop_wiring'])
        else:
            self._brokerTopicDisplay.clear()

        self._readJson()
        self.reloadPropPinsDisplay.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onReloadPropPinsDisplay(self):

        while self._pinsGridLayout.count():
            layout_item = self._pinsGridLayout.takeAt(0)
            if layout_item.widget():
                layout_item.widget().deleteLater()
            if layout_item.layout():
                layout_item.layout().deleteLater()
            del layout_item

        self._pinsGridLayout.addWidget(QLabel(self.tr("Output")), self._pinsGridLayout.rowCount(), 0, Qt.AlignHCenter)
        self._pinsGridLayout.addWidget(QLabel(self.tr("Variable")), self._pinsGridLayout.rowCount() - 1, 1,
                                       Qt.AlignHCenter)
        self._pinsGridLayout.addWidget(QLabel(self.tr("Initial")), self._pinsGridLayout.rowCount() - 1, 2,
                                       Qt.AlignHCenter)
        self._pinsGridLayout.addWidget(QLabel(self.tr("HIGH")), self._pinsGridLayout.rowCount() - 1, 3, Qt.AlignHCenter)
        self._pinsGridLayout.addWidget(QLabel(self.tr("LOW")), self._pinsGridLayout.rowCount() - 1, 4, Qt.AlignHCenter)

        for p, _ in self._boardPins:
            button = QPushButton(" {} ".format(p))
            button.released.connect(self.onPinConfiguration)
            if p in self._propPins:
                variable = self._propPins[p].getVariable()
                if self._propPins[p].getInitial() == GPIO_HIGH:
                    initial = 'HIGH'
                else:
                    initial = 'LOW'
                alias_high, alias_low = self._propPins[p].getAlias()
            else:
                variable, initial, alias_high, alias_low = ['-'] * 4
            self._pinsGridLayout.addWidget(button, self._pinsGridLayout.rowCount(), 0)
            self._pinsGridLayout.addWidget(QLabel(variable), self._pinsGridLayout.rowCount() - 1, 1, Qt.AlignHCenter)
            self._pinsGridLayout.addWidget(QLabel(initial), self._pinsGridLayout.rowCount() - 1, 2, Qt.AlignHCenter)
            self._pinsGridLayout.addWidget(QLabel(alias_high), self._pinsGridLayout.rowCount() - 1, 3, Qt.AlignHCenter)
            self._pinsGridLayout.addWidget(QLabel(alias_low), self._pinsGridLayout.rowCount() - 1, 4, Qt.AlignHCenter)

    # __________________________________________________________________
    def pinsByVariable(self):

        pins_by_variable = {}
        for _, pin in self._propPins.items():
            pins_by_variable[pin.getVariable()] = pin

        return OrderedDict(sorted(pins_by_variable.items()))

    # __________________________________________________________________
    def pinToKey(self, p):

        for key, pin in self._boardPins:
            if p == pin:
                return key
        return None

    # __________________________________________________________________
    @pyqtSlot()
    def print(self):

        html = HTML
        table = TABLE
        for key, _ in self._boardPins:
            row = ROW
            variable = '-'
            initial = '-'
            low = '-'
            high = '-'
            if key in self._propPins:
                variable = self._propPins[key].getVariable()
                if self._propPins[key].getInitial():
                    initial = 'HIGH'
                else:
                    initial = 'LOW'
                high, low = self._propPins[key].getAlias()
            row = row.replace('{{OUTPUT}}', key)
            row = row.replace('{{VARIABLE}}', variable)
            row = row.replace('{{INITIAL}}', initial)
            row = row.replace('{{HIGH}}', low)
            row = row.replace('{{LOW}}', high)
            table = table.replace('{{ROWS}}', row + "\n{{ROWS}}")
        table = table.replace('{{ROWS}}', "")
        title = TITLE
        title = title.replace('{{PROP}}', self._propSettings['prop']['prop_name'])
        title = title.replace('{{FILE}}', self._localFile)
        body = title
        body = body + table
        html = html.replace('{{BODY}}', body)
        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if dialog.exec_() == True:
            doc.print_(printer)

    # __________________________________________________________________
    @pyqtSlot()
    def upload(self):

        if self._propSettings['prop']['board'] == 'mega':
            self.uploadForMega()
            return

        pin_list = []
        for key, pin in self._boardPins:
            if key in self._propPins:
                pin_dict = {}
                pin_dict['pin'] = pin
                pin_dict['variable'] = self._propPins[key]._variable
                pin_dict['initial'] = self._propPins[key]._initial
                pin_dict['alias'] = self._propPins[key]._alias
                pin_list.append(pin_dict)

        settings = json.dumps(pin_list, ensure_ascii=False)
        self.publishRetainedMessage.emit(self._propSettings['prop']['prop_wiring'], settings)

    # __________________________________________________________________
    @pyqtSlot()
    def uploadForMega(self):

        # to stress the Mega memory, configure all pins
        # self.uploadFullMega()
        # return

        for key, pin in self._boardMegaPins:  # D0 and D1 must be cleared if set from previous config with no bridge
            pin_topic = self._propSettings['prop']['prop_wiring'] + '/' + pin
            self.publishRetainedMessage.emit(pin_topic, None)  # remove retained message

        self.publishMessage.emit(self._propSettings['prop']['prop_inbox'], 'clear:all')  # so the prop clears its pins

        for key, pin in self._boardPins:
            if key in self._propPins:
                pin_dict = {}
                pin_dict['p'] = int(pin[1:])  # integer (for Pi it's string)
                pin_dict['v'] = self._propPins[key]._variable
                pin_dict['i'] = self._propPins[key]._initial
                pin_dict['a'] = self._propPins[key]._alias
                pin_json = json.dumps(pin_dict, ensure_ascii=False)
                pin_topic = self._propSettings['prop']['prop_wiring'] + '/' + pin
                self.publishRetainedMessage.emit(pin_topic, pin_json)

    # __________________________________________________________________
    @pyqtSlot()
    def uploadFullMega(self):

        for key, pin in self._boardMegaPins:
            pin_topic = self._propSettings['prop']['prop_wiring'] + '/' + pin
            self.publishRetainedMessage.emit(pin_topic, None)

        self.publishMessage.emit(self._propSettings['prop']['prop_inbox'], 'clear:all')

        for key, pin in self._boardPins:
            pin_topic = self._propSettings['prop']['prop_wiring'] + '/' + pin
            pin_dict = {}
            pin_dict['p'] = int(pin[1:])
            pin_dict['v'] = "var/" + str(int(pin[1:]))
            pin_dict['i'] = False
            pin_dict['a'] = ("on", "off")
            pin_json = json.dumps(pin_dict, ensure_ascii=False)
            self.publishRetainedMessage.emit(pin_topic, pin_json)
