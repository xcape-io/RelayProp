#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ControlSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure control parameters.
"""

from HelpDialog import HelpDialog
from constants import *

try:
    MEGA_YUN_ONLY
    MEGA_YUN_SUPPORTED = MEGA_YUN_ONLY
except NameError:
    MEGA_YUN_SUPPORTED = True
try:
    PI_MPC23017_NOT_SUPPORTED
    PI_MPC23017_SUPPORTED = not PI_MPC23017_NOT_SUPPORTED
except NameError:
    PI_MPC23017_SUPPORTED = True

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QRadioButton, QPushButton, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QCheckBox, QFileDialog
from PyQt5.QtGui import QIcon
import re, sys, os
import codecs, configparser

class ControlSettingsDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, prop_settings, logger):

        super(ControlSettingsDialog, self).__init__()

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
        self._boardPiButton = QRadioButton(self.tr("Raspberry Pi"))
        self._boardPiExpanderButton = QCheckBox(self.tr("Raspberry Pi with MCP23017 expander"))
        board_box_layout.addWidget(self._boardMegaButton)
        board_box_layout.addWidget(self._boardMegaYunButton)
        board_box_layout.addWidget(self._boardPiButton)
        board_box_layout.addWidget(self._boardPiExpanderButton)

        self._loadButton = QPushButton(" {} ".format(self.tr("Load from prop configuration")))
        self._loadButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        board_box_layout.addWidget(self._loadButton)

        self._paramWidget = QWidget()
        self._paramWidget.setContentsMargins(0, 0, 0, 0)
        param_layout = QGridLayout(self._paramWidget)
        param_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._paramWidget)

        prop_name_label = QLabel(self.tr("Prop name"))
        param_layout.addWidget(prop_name_label, param_layout.rowCount(), 0)
        self._propNameInput = QLineEdit()
        param_layout.addWidget(self._propNameInput, param_layout.rowCount() - 1, 1)

        self._propNameInput.editingFinished.connect(self.onPropNameEditingFinished)

        prop_inbox_label = QLabel(self.tr("Prop inbox"))
        param_layout.addWidget(prop_inbox_label, param_layout.rowCount(), 0)
        self._propInboxInput = QLineEdit()
        param_layout.addWidget(self._propInboxInput, param_layout.rowCount() - 1, 1)

        prop_outbox_label = QLabel(self.tr("Prop outbox"))
        param_layout.addWidget(prop_outbox_label, param_layout.rowCount(), 0)
        self._propOutboxInput = QLineEdit()
        param_layout.addWidget(self._propOutboxInput, param_layout.rowCount() - 1, 1)

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
        broker_box_layout.addWidget(self._brokerIpAddressInput, broker_box_layout.rowCount() - 1, 1)

        broker_port_label = QLabel(self.tr("Broker IP port"))
        broker_box_layout.addWidget(broker_port_label, broker_box_layout.rowCount(), 0)
        self._brokerIpPortInput = QLineEdit()
        broker_box_layout.addWidget(self._brokerIpPortInput, broker_box_layout.rowCount() - 1, 1)

        options_box = QGroupBox(self.tr("Options"))
        options_box_layout = QVBoxLayout(options_box)
        main_layout.addWidget(options_box)

        self._alwaysOnTopButton = QCheckBox(self.tr("Applet window always on top (active at next start)"))
        options_box_layout.addWidget(self._alwaysOnTopButton)

        self._editHiddenButton = QCheckBox(self.tr("Hide edit button"))
        options_box_layout.addWidget(self._editHiddenButton)

        self._connectionStatusHiddenButton = QCheckBox(self.tr("Hide connection status"))
        options_box_layout.addWidget(self._connectionStatusHiddenButton)

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
        self._loadButton.released.connect(self.onLoad)

        self.fillSettings(self._propSettings )

    # __________________________________________________________________
    def closeEvent(self, e):

        self.onClose()

    # __________________________________________________________________
    def fillSettings(self, prop_settings):

        if 'board' not in prop_settings['prop']:
            self._paramWidget.setDisabled(True)
            self._loadButton.setEnabled(True)
            self._boardMegaYunButton.setDisabled(True or not MEGA_YUN_SUPPORTED)  # True
            self._boardPiExpanderButton.setDisabled(True)
        else:
            self._loadButton.setDisabled(True)
            if prop_settings['prop']['board'] == 'mega':
                self._boardMegaButton.setChecked(True)
                self._boardMegaYunButton.setEnabled(False and MEGA_YUN_SUPPORTED)  # True
                self._boardPiExpanderButton.setEnabled(False)
            else:
                self._boardPiButton.setChecked(True)
                self._boardPiExpanderButton.setEnabled(PI_MPC23017_SUPPORTED)  # True
                self._boardMegaYunButton.setEnabled(False)

            if 'mega_bridge' in prop_settings['prop'] and prop_settings['prop']['mega_bridge'] == '1':
                self._boardMegaYunButton.setChecked(True)
            else:
                self._boardMegaYunButton.setChecked(not MEGA_YUN_SUPPORTED)  # False

            if 'pi_expander' in prop_settings['prop'] and prop_settings['prop']['pi_expander'] == '1':
                self._boardPiExpanderButton.setChecked(PI_MPC23017_SUPPORTED)  # True
            else:
                self._boardPiExpanderButton.setChecked(False)

            if 'prop_name' in prop_settings['prop']:
                self._propNameInput.setText(prop_settings['prop']['prop_name'])

            if 'prop_inbox' in prop_settings['prop']:
                self._propInboxInput.setText(prop_settings['prop']['prop_inbox'])

            if 'prop_outbox' in prop_settings['prop']:
                self._propOutboxInput.setText(prop_settings['prop']['prop_outbox'])

            if 'prop_settings' in prop_settings['prop']:
                self._propSettingsInput.setText(prop_settings['prop']['prop_settings'])

            if 'broker_address' in prop_settings['prop']:
                self._brokerIpAddressInput.setText(prop_settings['prop']['broker_address'])
            else:
                self._brokerIpAddressInput.setText('localhost')

            if 'broker_port' in prop_settings['prop']:
                self._brokerIpPortInput.setText(prop_settings['prop']['broker_port'])
            else:
                self._brokerIpPortInput.setText('1883')

        if 'options' in prop_settings:
            if 'always_on_top' in prop_settings['options'] and prop_settings['options']['always_on_top'] == '1':
                self._alwaysOnTopButton.setChecked(True)
            else:
                self._alwaysOnTopButton.setChecked(False)
            if 'edit' in prop_settings['options'] and prop_settings['options']['edit'] == '0':
                self._editHiddenButton.setChecked(True)
            else:
                self._editHiddenButton.setChecked(False)
            if 'connection_status' in prop_settings['options'] and prop_settings['options']['connection_status'] == '0':
                self._connectionStatusHiddenButton.setChecked(True)
            else:
                self._connectionStatusHiddenButton.setChecked(False)


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

        if 'options' not in self._propSettings.sections():
            self._propSettings.add_section('options')

        if self._alwaysOnTopButton.isChecked():
            self._propSettings['options']['always_on_top'] = '1'
        else:
            self._propSettings['options']['always_on_top'] = '0'

        if self._editHiddenButton.isChecked():
            self._propSettings['options']['edit'] = '0'
        else:
            self._propSettings['options']['edit'] = '1'

        if self._connectionStatusHiddenButton.isChecked():
            self._propSettings['options']['connection_status'] = '0'
        else:
            self._propSettings['options']['connection_status'] = '1'

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
    def onLoad(self):

        dlg = QFileDialog(self,
                          self.tr("Select prop configuration .ini file"),
                          os.getcwd(),
                          self.tr("Configuration files (*.ini);; All files (*.*)"))

        dlg.setViewMode(QFileDialog.Detail)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.selectFile('prop.ini')

        ret = dlg.exec()

        if QDialog.Accepted == ret and len(dlg.selectedFiles()) == 1:
            returned_path = dlg.selectedFiles()[0]
        else:
            return

        if os.path.isfile(returned_path):
            prop_settings = configparser.ConfigParser()
            prop_settings.read_file(codecs.open(returned_path, 'r', 'utf8'))
            if 'prop' not in prop_settings.sections():
                return
            
            self._propSettings = prop_settings

            with open('prop.ini', 'w') as configfile:
                self._propSettings.write(configfile)
    
            self.fillSettings(self._propSettings)
            if not self._paramWidget.isEnabled():
                self._paramWidget.setEnabled(True)
                self._loadButton.setDisabled(True)

    # __________________________________________________________________
    @pyqtSlot()
    def onBoardMegaButton(self):

        self._logger.info(self.tr("Settings : set 'Mega' board"))
        self.setWindowIcon(QIcon('./images/arduino.svg'))
        self._boardMegaYunButton.setEnabled(False and MEGA_YUN_SUPPORTED)  # True
        self._boardPiExpanderButton.setEnabled(False)
        if not self._paramWidget.isEnabled():
            self._paramWidget.setEnabled(True)
            self._loadButton.setDisabled(True)
            self._propNameInput.setText('Relay Mega')
            self.onPropNameEditingFinished()

    # __________________________________________________________________
    @pyqtSlot()
    def onBoardPiButton(self):

        self._logger.info(self.tr("Settings : set 'Pi' board"))
        self.setWindowIcon(QIcon('./images/raspberry-pi.svg'))
        self._boardPiExpanderButton.setEnabled(PI_MPC23017_SUPPORTED)  # True
        self._boardMegaYunButton.setEnabled(False)
        if not self._paramWidget.isEnabled():
            self._paramWidget.setEnabled(True)
            self._loadButton.setDisabled(True)
            self._propNameInput.setText('Relay Pi')
            self.onPropNameEditingFinished()

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
                self._propInboxInput.setText(
                    inbox.replace("/{}/inbox".format(previous[0]), "/{}/inbox".format(prop_name)))

        if not self._propOutboxInput.text().strip():
            self._propOutboxInput.setText('Room/My room/Props/' + prop_name + '/outbox')
        else:
            outbox = self._propOutboxInput.text()
            previous = re.findall(r'([\s\w]+)/outbox$', outbox)
            if previous:
                self._propOutboxInput.setText(
                    outbox.replace("/{}/outbox".format(previous[0]), "/{}/outbox".format(prop_name)))

        if not self._propSettingsInput.text().strip():
            self._propSettingsInput.setText('Room/My room/Props/' + prop_name + '/settings')
        else:
            settings = self._propSettingsInput.text()
            previous = re.findall(r'([\s\w]+)/settings$', settings)
            if previous:
                self._propSettingsInput.setText(
                    settings.replace("/{}/settings".format(previous[0]), "/{}/settings".format(prop_name)))
