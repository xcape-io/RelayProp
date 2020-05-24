#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PropSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure panel parameters.
"""

from HelpDialog import HelpDialog

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QPushButton, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtGui import QIcon
import os, re, sys
from constants import *


class PropSettingsDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, prop_settings, logger):

        super(PropSettingsDialog, self).__init__()

        self._logger = logger
        self._propSettings = prop_settings

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Configuration"))

        if 'board' not in self._propSettings['prop']:
            self.setWindowIcon(QIcon('./mqtticon.png'))
        elif self._propSettings['prop']['board'] == 'mega':
            self.setWindowIcon(QIcon('./images/arduino.svg'))
        else:
            self.setWindowIcon(QIcon('./images/raspberry-pi.svg'))

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        board_box = QGroupBox(self.tr("Prop board model"))
        board_box_layout = QVBoxLayout(board_box)
        main_layout.addWidget(board_box)

        self._boardMegaButton = QRadioButton(self.tr("Arduino Mega 2560"))
        self._boardMegaYunButton = QCheckBox(self.tr("Arduino Mega 2560 with Dragino Yún shield"))
        self._boardMegaYunButton.setEnabled(False)
        self._boardPiButton = QRadioButton(self.tr("Raspberry Pi"))
        self._boardPiExpanderButton = QCheckBox(self.tr("Raspberry Pi with MCP23017 expander"))
        self._boardPiExpanderButton.setEnabled(False)
        board_box_layout.addWidget(self._boardMegaButton)
        board_box_layout.addWidget(self._boardMegaYunButton)
        board_box_layout.addWidget(self._boardPiButton)
        board_box_layout.addWidget(self._boardPiExpanderButton)

        self._paramWidget = QWidget()
        self._paramWidget.setContentsMargins(0,0,0,0)
        param_layout = QGridLayout(self._paramWidget)
        param_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self._paramWidget)

        prop_name_label = QLabel(self.tr("Prop name"))
        param_layout.addWidget(prop_name_label, param_layout.rowCount(), 0)
        self._propNameInput = QLineEdit()
        param_layout.addWidget(self._propNameInput , param_layout.rowCount() - 1, 1)

        self._propNameInput.editingFinished.connect(self.onPropNameEditingFinished)

        prop_inbox_label = QLabel(self.tr("Prop inbox"))
        param_layout.addWidget(prop_inbox_label, param_layout.rowCount(), 0)
        self._propInboxInput = QLineEdit()
        param_layout.addWidget(self._propInboxInput , param_layout.rowCount() - 1, 1)

        prop_outbox_label = QLabel(self.tr("Prop outbox"))
        param_layout.addWidget(prop_outbox_label, param_layout.rowCount(), 0)
        self._propOutboxInput = QLineEdit()
        param_layout.addWidget(self._propOutboxInput , param_layout.rowCount() - 1, 1)

        prop_settings_label = QLabel(self.tr("Prop settings"))
        param_layout.addWidget(prop_settings_label, param_layout.rowCount(), 0)
        self._propSettingsInput = QLineEdit()
        param_layout.addWidget(self._propSettingsInput, param_layout.rowCount() - 1, 1)

        broker_box = QGroupBox(self.tr("MQTT broker"))
        broker_box.setFlat(True)
        broker_box_layout = QGridLayout(broker_box)
        main_layout.addWidget(broker_box)

        broker_address_label = QLabel(self.tr("Broker IP address"))
        broker_box_layout.addWidget(broker_address_label, broker_box_layout.rowCount(), 0)
        self._brokerIpAddressInput = QLineEdit()
        broker_box_layout.addWidget(self._brokerIpAddressInput , broker_box_layout.rowCount() - 1, 1)

        broker_port_label = QLabel(self.tr("Broker IP port"))
        broker_box_layout.addWidget(broker_port_label, broker_box_layout.rowCount(), 0)
        self._brokerIpPortInput = QLineEdit()
        broker_box_layout.addWidget(self._brokerIpPortInput, broker_box_layout.rowCount() - 1, 1)

        apply_button = QPushButton(self.tr("Apply"))
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cancel_button = QPushButton(self.tr("Cancel"))
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        help_button = QPushButton(self.tr("Help"))
        help_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.addWidget(help_button)
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self._boardMegaButton.released.connect(self.onBoardMegaButton)
        self._boardPiButton.released.connect(self.onBoardPiButton)
        apply_button.released.connect(self.onApply)
        cancel_button.released.connect(self.onClose)
        help_button.released.connect(self.onHelp)

        if 'board' not in self._propSettings['prop']:
            self._paramWidget.setDisabled(True)
        else:
            if self._propSettings['prop']['board'] == 'mega':
                self._boardMegaButton.setChecked(True)
                self._boardMegaYunButton.setEnabled(True)
                self._boardPiExpanderButton.setEnabled(False)
            else:
                self._boardPiButton.setChecked(True)
                self._boardPiExpanderButton.setEnabled(True)
                self._boardMegaYunButton.setEnabled(False)

            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                self._boardMegaYunButton.setChecked(True)
            else:
                self._boardMegaYunButton.setChecked(False)

            if 'pi_expander' in self._propSettings['prop'] and self._propSettings['prop']['pi_expander'] == '1':
                self._boardPiExpanderButton.setChecked(True)
            else:
                self._boardPiExpanderButton.setChecked(False)

            if 'prop_name' in self._propSettings['prop']:
                self._propNameInput.setText(self._propSettings['prop']['prop_name'])

            if 'prop_inbox' in self._propSettings['prop']:
                self._propInboxInput.setText(self._propSettings['prop']['prop_inbox'])

            if 'prop_outbox' in self._propSettings['prop']:
                self._propOutboxInput.setText(self._propSettings['prop']['prop_outbox'])

            if 'prop_settings' in self._propSettings['prop']:
                self._propSettingsInput.setText(self._propSettings['prop']['prop_settings'])

            if 'broker_address' in self._propSettings['prop']:
                self._brokerIpAddressInput.setText(self._propSettings['prop']['broker_address'])
            else:
                self._brokerIpAddressInput.setText('localhost')

            if 'broker_port' in self._propSettings['prop']:
                self._brokerIpPortInput.setText(self._propSettings['prop']['broker_port'])
            else:
                self._brokerIpPortInput.setText('1883')


    # __________________________________________________________________
    def closeEvent(self, e):

        self.onClose()

    # __________________________________________________________________
    def forceBoardModel(self):

        msg = QMessageBox()
        msg.setWindowIcon(self.windowIcon())
        msg.setIcon(QMessageBox.Warning)
        msg.setText(self.tr("Please choose a board model."))
        msg.setWindowTitle(self.tr("Board model required"))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # __________________________________________________________________
    @pyqtSlot()
    def onApply(self):

        if not self._boardMegaButton.isChecked() and not self._boardPiButton.isChecked():
            self.forceBoardModel()
            return

        if self._boardMegaButton.isChecked():
            self._propSettings['prop']['board'] = "mega"
        else:
            self._propSettings['prop']['board'] = "pi"

        if self._boardMegaYunButton.isChecked():
            self._propSettings['prop']['mega_bridge'] = "1"
        else:
            self._propSettings['prop']['mega_bridge'] = "0"

        if self._boardPiExpanderButton.isChecked():
            self._propSettings['prop']['pi_expander'] = "1"
        else:
            self._propSettings['prop']['pi_expander'] = "0"

        self._propSettings['prop']['prop_name'] = self._propNameInput.text().strip()
        self._propSettings['prop']['prop_inbox'] = self._propInboxInput.text().strip()
        self._propSettings['prop']['prop_outbox'] = self._propOutboxInput.text().strip()
        self._propSettings['prop']['prop_settings'] = self._propSettingsInput.text().strip()

        self._propSettings['prop']['broker_address'] = self._brokerIpAddressInput.text().strip()

        broker_port = self._brokerIpPortInput.text().strip()
        if broker_port.isdigit():
            self._propSettings['prop']['broker_port'] = broker_port
        else:
            self._propSettings['prop']['broker_port'] = ""

        if self._propSettings['prop']['board'] == 'mega':
            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                self._propSettings['prop']['json'] = os.path.abspath(LOCAL_ARDUINO_MEGA2560_BRIDGE_JSON)
            else:
                self._propSettings['prop']['json'] = os.path.abspath(LOCAL_ARDUINO_MEGA2560_JSON)
        else:
            if 'pi_expander' in self._propSettings['prop'] and self._propSettings['prop']['pi_expander'] == '1':
                self._propSettings['prop']['json'] = os.path.abspath(LOCAL_PI_MCP23017_JSON)
            else:
                self._propSettings['prop']['json'] = os.path.abspath(LOCAL_PI_JSON)

        with open('prop.ini', 'w') as configfile:
            self._propSettings.write(configfile)

        self.accept()

    # __________________________________________________________________
    @pyqtSlot()
    def onClose(self):

        if not self._boardMegaButton.isChecked() and not self._boardPiButton.isChecked():
            sys.exit(-10)

        self.accept()

    # __________________________________________________________________
    @pyqtSlot()
    def onHelp(self):

        dlg = HelpDialog(self.tr("Configure the central prop"), './help/configure.html')
        dlg.exec()

    # __________________________________________________________________
    @pyqtSlot()
    def onBoardMegaButton(self):

        self._logger.info(self.tr("Settings : set 'Mega' board"))
        self.setWindowIcon(QIcon('./images/arduino.svg'))
        self._boardMegaYunButton.setEnabled(True)
        self._boardPiExpanderButton.setEnabled(False)
        if not self._paramWidget.isEnabled():
            self._paramWidget.setEnabled(True)
            self._propNameInput.setText('Relay Mega')
            self.onPropNameEditingFinished()
        if not self._brokerIpPortInput.text():
            self._brokerIpPortInput.setText('1883')

    # __________________________________________________________________
    @pyqtSlot()
    def onBoardPiButton(self):

        self._logger.info(self.tr("Settings : set 'Pi' board"))
        self.setWindowIcon(QIcon('./images/raspberry-pi.svg'))
        self._boardPiExpanderButton.setEnabled(True)
        self._boardMegaYunButton.setEnabled(False)
        if not self._paramWidget.isEnabled():
            self._paramWidget.setEnabled(True)
            self._propNameInput.setText('Relay Pi')
            self.onPropNameEditingFinished()
        if not self._brokerIpPortInput.text():
            self._brokerIpPortInput.setText('1883')

    # __________________________________________________________________
    @pyqtSlot()
    def onPropNameEditingFinished(self):

        if not self._propNameInput.text():
            if self._boardMegaButton.isChecked():
                self._propNameInput.setText('Relay Mega')
            else:
                self._propNameInput.setText('Relay Pi')

        prop_name = self._propNameInput.text().strip()

        if not self._propInboxInput.text().strip():
            self._propInboxInput.setText('Room/My room/Props/' + prop_name + '/inbox')
        else:
            inbox = self._propInboxInput.text()
            previous = re.findall(r'([\s\w]+)/inbox$', inbox)
            if previous:
                self._propInboxInput.setText(inbox.replace("/{}/inbox".format(previous[0]), "/{}/inbox".format(prop_name)))

        if not self._propOutboxInput.text().strip():
            self._propOutboxInput.setText('Room/My room/Props/' + prop_name + '/outbox')
        else:
            outbox = self._propOutboxInput.text()
            previous = re.findall(r'([\s\w]+)/outbox$', outbox)
            if previous:
                self._propOutboxInput.setText(outbox.replace("/{}/outbox".format(previous[0]), "/{}/outbox".format(prop_name)))

        if not self._propSettingsInput.text().strip():
            self._propSettingsInput.setText('Room/My room/Props/' + prop_name + '/settings')
        else:
            settings = self._propSettingsInput.text()
            previous = re.findall(r'([\s\w]+)/settings$', settings)
            if previous:
                self._propSettingsInput.setText(settings.replace("/{}/settings".format(previous[0]), "/{}/settings".format(prop_name)))
