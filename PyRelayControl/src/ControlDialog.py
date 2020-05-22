#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ControlDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to control PanelProps app running on Raspberry.
"""

import os, yaml
import re

from constants import *
from PropPanel import PropPanel
from ControlSettingsDialog import ControlSettingsDialog
from PanelSettingsDialog import PanelSettingsDialog
from AppletDialog import AppletDialog
from LedWidget import LedWidget
from PinGroupButton import PinGroupButton
from PinSwitch import PinSwitch

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QPoint
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QGroupBox, QDialog


class ControlDialog(AppletDialog):
    aboutToClose = pyqtSignal()
    propDataReveived = pyqtSignal(dict)
    publishMessage = pyqtSignal(str, str)
    resetBrokerConnection = pyqtSignal()
    switchLed = pyqtSignal(str, str)

    # __________________________________________________________________
    def __init__(self, title, icon, prop_settings, logger):

        # members required by _buildUi() must be set before calling super().__init__()
        self._propSettings = prop_settings
        self._groupBoxes = {}

        if 'prop' in self._propSettings and 'json' in self._propSettings['prop']:
            self._propVariables = PropPanel.getJson(self._propSettings['prop']['json'], logger)
        else:
            self._propVariables = {}

        super().__init__(title, icon, logger)

        self._reDataSplitValues = re.compile(r'[^\s]+\s*=')
        self._reDataVariables = re.compile(r'([^\s]+)\s*=')

        if 'options' in self._propSettings and 'always_on_top' in self._propSettings['options'] and \
                self._propSettings['options']['always_on_top'] == '1':
            self.setAttribute(Qt.WA_AlwaysStackOnTop)
            self.setWindowFlags(self.windowFlags()
                                & ~Qt.WindowContextHelpButtonHint | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    # __________________________________________________________________
    @pyqtSlot()
    def _buildPropWidgets(self):

        for group in list(self._groupBoxes.keys()):
            widgets = self._groupBoxes[group].findChildren(PinSwitch, '', options=Qt.FindChildrenRecursively)
            for w in widgets:
                try:
                    self._groupBoxes[group].layout().removeWidget(w)
                    w.deleteLater()
                except Exception as e:
                    print(e)
            del (widgets)
            self._mainLayout.removeWidget(self._groupBoxes[group])
            self._groupBoxes[group].deleteLater()
            del (self._groupBoxes[group])

        for v, pin in self._propVariables.items():
            if '/' in v:
                group, variable = v.split('/', 1)
            else:
                group = None
                variable = v
            switch = PinSwitch(label=variable.capitalize(),
                               variable=pin.getVariable(),
                               image_on=DATALED_IMAGE_ON,
                               image_off=DATALED_IMAGE_OFF,
                               sync=pin.getVariable(),
                               sync_on=pin.getHigh(),
                               sync_off=pin.getLow(),
                               action_on=pin.getOff(),
                               action_off=pin.getOn(),
                               value_on=pin.getHigh(),
                               value_off=pin.getLow(),
                               topic=self._propSettings['prop']['prop_inbox'])
            if group in self._groupBoxes:
                self._groupBoxes[group].layout().addWidget(switch)
            else:
                caption = group.capitalize() if group is not None else ''
                box = QGroupBox(caption)
                box_layout = QVBoxLayout(box)
                box_layout.setSpacing(12)
                self._groupBoxes[group] = box
                self._mainLayout.addWidget(box)
                box_layout.addWidget(switch)
            switch.publishMessage.connect(self.publishMessage)
            self.propDataReveived.connect(switch.onDataReceived)

        for group in list(self._groupBoxes.keys()):
            if group is None: continue
            button_on = PinGroupButton(group, GPIO_HIGH, self._propSettings['prop']['prop_inbox'])
            self._groupBoxes[group].layout().addWidget(button_on)

            button_off = PinGroupButton(group, GPIO_LOW, self._propSettings['prop']['prop_inbox'])
            self._groupBoxes[group].layout().addWidget(button_off)

            button_on.publishMessage.connect(self.publishMessage)
            button_off.publishMessage.connect(self.publishMessage)

    # __________________________________________________________________
    def _buildUi(self):

        self._mainLayout = QVBoxLayout()
        self._mainLayout.setSpacing(12)

        if 'prop_name' in self._propSettings['prop']:
            prop_name = self._propSettings['prop']['prop_name']
        else:
            prop_name = 'Prop'

        self._led = LedWidget(prop_name, QSize(40, 20))
        self._led.setRedAsBold(True)
        self._led.setRedAsRed(True)
        self._led.switchOn('gray')

        self._settingsButton = QPushButton()
        self._settingsButton.setFlat(True)
        self._settingsButton.setToolTip(self.tr("Prop configuration"))
        self._settingsButton.setIconSize(QSize(20, 20))
        self._settingsButton.setFixedSize(QSize(28, 28))
        self._settingsButton.pressed.connect(self.onPropConfiguration)

        if self._propSettings['prop']['board'] == 'mega':
            self._settingsButton.setIcon(QIcon('./images/arduino.svg'))
        else:
            self._settingsButton.setIcon(QIcon('./images/raspberry-pi.svg'))

        self._editButton = QPushButton()
        self._editButton.setIcon(QIcon('./images/cog-black.svg'))
        self._editButton.setFlat(True)
        self._editButton.setToolTip(self.tr("Edit panel"))
        self._editButton.setIconSize(QSize(16, 16))
        self._editButton.setFixedSize(QSize(20, 20))
        self._editButton.pressed.connect(self.onPanelEdition)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(2)
        header_layout.addSpacing(10)
        header_layout.addWidget(self._led)
        header_layout.addWidget(self._editButton, Qt.AlignRight)
        header_layout.addWidget(self._settingsButton, Qt.AlignRight)
        self._mainLayout.addLayout(header_layout)

        if 'options' in self._propSettings:
            if 'edit' in self._propSettings['options'] and self._propSettings['options']['edit'] == '0':
                self._editButton.setVisible(False)

        self._mainLayout.addStretch(0)

        self.setLayout(self._mainLayout)

        self.switchLed.connect(self._led.switchOn)

        self._buildPropWidgets()

    # __________________________________________________________________
    @pyqtSlot()
    def layoutLoadSettings(self):

        if os.path.isfile(LAYOUT_FILE):
            with open(LAYOUT_FILE, 'r') as layoutfile:
                layout = yaml.load(layoutfile, Loader=yaml.SafeLoader)

            self.move(QPoint(layout['x'], layout['y']))
            self.resize(QSize(layout['w'], layout['h']))

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
                    i = i+1
        except Exception as e:
            self._logger.debug(e)

        self.propDataReveived.emit(variables)

    # __________________________________________________________________
    def closeEvent(self, e):

        self.aboutToClose.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onConnectedToMqttBroker(self):

        if self._led.color() == 'red':
            if 'prop_name' in self._propSettings['prop']:
                if 'options' in self._propSettings:
                    if 'connection_status' in self._propSettings['options'] and self._propSettings['options'][
                        'connection_status'] == '0':
                        self._led.switchOn('yellow', self._propSettings['prop']['prop_name'])
                    else:
                        self._led.switchOn('yellow', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                                       self.tr("connected")))
            else:
                self._led.switchOn('yellow')

    # __________________________________________________________________
    @pyqtSlot()
    def onDisconnectedToMqttBroker(self):

        if 'prop_name' in self._propSettings['prop']:
            if 'options' in self._propSettings:
                if 'connection_status' in self._propSettings['options'] and self._propSettings['options']['connection_status'] == '0':
                    self._led.switchOn('red', '')
                else:
                    self._led.switchOn('red', self.tr("MQTT broker not connected"))
        else:
            self._led.switchOn('red')

    # __________________________________________________________________
    @pyqtSlot(str, str)
    def onMessageReceived(self, topic, message):

        if message.startswith("DISCONNECTED"):
            if 'prop_name' in self._propSettings['prop']:
                if 'options' in self._propSettings:
                    if 'connection_status' in self._propSettings['options'] and self._propSettings['options'][
                        'connection_status'] == '0':
                        self._led.switchOn('yellow', self._propSettings['prop']['prop_name'])
                    else:
                        self._led.switchOn('yellow', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                                       self.tr("disconnected")))
            else:
                self._led.switchOn('yellow')
        else:
            if self._led.color() != 'green':
                if 'prop_name' in self._propSettings['prop']:
                    if 'options' in self._propSettings:
                        if 'connection_status' in self._propSettings['options'] and self._propSettings['options'][
                            'connection_status'] == '0':
                            self._led.switchOn('green', self._propSettings['prop']['prop_name'])
                        else:
                            self._led.switchOn('green', "{} ({}) ".format(self._propSettings['prop']['prop_name'],
                                                                           self.tr("connected")))
                else:
                    self._led.switchOn('green')

        if 'prop_outbox' in self._propSettings['prop']:
            if topic == self._propSettings['prop']['prop_outbox'] and message.startswith('DATA '):
                self._parsePropData(message)

    # __________________________________________________________________
    @pyqtSlot()
    def onPanelEdition(self):

        dlg = PanelSettingsDialog(self._propVariables, self._propSettings, self._logger)
        dlg.setModal(True)

        dlg.rebuildWidgets.connect(self._buildPropWidgets)

        dlg.exec()

    # __________________________________________________________________
    @pyqtSlot()
    def onPropConfiguration(self):

        dlg = ControlSettingsDialog(self._propSettings, self._logger)
        dlg.setModal(True)
        if dlg.exec() == QDialog.Accepted:
            if 'prop_name' in self._propSettings['prop']:
                self._led._defaultText = self._propSettings['prop']['prop_name']
                if 'options' in self._propSettings:
                    if 'connection_status' in self._propSettings['options'] and self._propSettings['options']['connection_status'] == '0':
                        self._led.switchOn('red', '')
                    else:
                        self._led.switchOn('red', self.tr("MQTT broker not connected"))
            self.resetBrokerConnection.emit()

        if 'options' in self._propSettings:
            if 'edit' in self._propSettings['options'] and self._propSettings['options']['edit'] == '0':
                self._editButton.setVisible(False)
            else:
                self._editButton.setVisible(True)

        if self._propSettings['prop']['board'] == 'mega':
            self._settingsButton.setIcon(QIcon('./images/arduino.svg'))
        else:
            self._settingsButton.setIcon(QIcon('./images/raspberry-pi.svg'))
