#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PanelSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure control parameters.
"""

from constants import *
from PanelWidgetsEditor import PanelWidgetsEditor
from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton, QGroupBox, QSpacerItem
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon


class PanelSettingsDialog(QDialog):
    rebuildWidgets = pyqtSignal()
    wiringButtonReleased = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings,
                 widget_groups, widget_titles,
                 widget_variables, widget_images, widget_buttons,
                 widget_hiddens, relaunch_command, ssh_credentials, logger):

        super(PanelSettingsDialog, self).__init__()

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables
        self._widgetGroups = widget_groups
        self._widgetTitles = widget_titles
        self._widgetVariables = widget_variables
        self._widgetImages = widget_images
        self._widgetButtons = widget_buttons
        self._widgetHiddens = widget_hiddens
        self._relaunchCommand = relaunch_command
        self._sshCredentials = ssh_credentials

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Settings"))

        self.setWindowIcon(QIcon('./x-settings.png'))

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        wiring_button = QPushButton(self.tr("Wiring configuration"))
        wiring_button.setToolTip(self.tr("Show/Hide wiring configuration"))
        wiring_button.setFocusPolicy(Qt.NoFocus)

        main_layout.addWidget(wiring_button)

        wiring_button.released.connect(self.wiringButtonReleased)
        wiring_button.released.connect(self.accept)

        if self._propVariables:
            button = self.tr("Rebuild panel from new wiring")
        else:
            button = self.tr("Build panel from wiring")

        build_button = QPushButton(" {} ".format(button))
        build_button.setFocusPolicy(Qt.NoFocus)

        main_layout.addWidget(build_button)

        credentials_box = QGroupBox(self.tr("Prop SSH credentials"))
        credentials_box.setToolTip(self.tr("Credentials for relaunch and reboot SSH commands"))
        credentials_box_layout = QGridLayout(credentials_box)
        main_layout.addWidget(credentials_box)

        self._addrInput = QLineEdit()
        credentials_box_layout.addWidget(QLabel(self.tr("IP address")), credentials_box_layout.rowCount(), 0)
        credentials_box_layout.addWidget(self._addrInput, credentials_box_layout.rowCount() - 1, 1)
        credentials_box_layout.addItem(QSpacerItem(200, 5), credentials_box_layout.rowCount() - 1, 2)

        self._userInput = QLineEdit()
        credentials_box_layout.addWidget(QLabel(self.tr("User")), credentials_box_layout.rowCount(), 0)
        credentials_box_layout.addWidget(self._userInput, credentials_box_layout.rowCount() - 1, 1)
        credentials_box_layout.addItem(QSpacerItem(200, 5), credentials_box_layout.rowCount() - 1, 2)

        self._paswInput = QLineEdit()
        credentials_box_layout.addWidget(QLabel(self.tr("Password")), credentials_box_layout.rowCount(), 0)
        credentials_box_layout.addWidget(self._paswInput, credentials_box_layout.rowCount() - 1, 1)

        if 'addr' in self._sshCredentials:
            self._addrInput.setText(self._sshCredentials['addr'])
        if 'user' in self._sshCredentials:
            self._userInput.setText(self._sshCredentials['user'])

        if 'pasw' in self._sshCredentials:
            if len(self._sshCredentials['pasw']):
                r = list(map(lambda x: chr(256 - int(x)), bytearray.fromhex(self._sshCredentials['pasw'])))
                self._paswInput.setText(''.join(r))
            else:
                self._paswInput.setText(self._sshCredentials['pasw'])

        self._addrInput.editingFinished.connect(self.onCredentialsEdition)
        self._userInput.editingFinished.connect(self.onCredentialsEdition)
        self._paswInput.editingFinished.connect(self.onCredentialsEdition)

        close_button = QPushButton(self.tr("Close"))
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        close_button.setFocusPolicy(Qt.NoFocus)

        edit_button = QPushButton(' {} '.format(self.tr("Edit captions and indicators")))
        edit_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        edit_button.setFocusPolicy(Qt.NoFocus)
        edit_button.setEnabled(len(self._propVariables))

        button_layout = QHBoxLayout()
        button_layout.addWidget(edit_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        close_button.released.connect(self.accept)
        edit_button.released.connect(self.onEdit)
        build_button.released.connect(self.onBuild)

    # __________________________________________________________________
    @pyqtSlot()
    def onBuild(self):

        if self._propSettings['prop']['board'] == 'mega':
            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                local_json = LOCAL_ARDUINO_MEGA2560_BRIDGE_JSON
            else:
                local_json = LOCAL_ARDUINO_MEGA2560_JSON
        else:
            if 'pi_expander' in self._propSettings['prop'] and self._propSettings['prop']['pi_expander'] == '1':
                local_json = LOCAL_PI_MCP23017_JSON
            else:
                local_json = LOCAL_PI_JSON

        prop_variables = PropPanel.getVariablesJson(local_json, self._logger)

        new_variables = []
        for variable in prop_variables:
            if variable not in self._propVariables:
                new_variables.append(variable)

        lost_variables = []
        for variable in self._propVariables:
            if variable not in prop_variables:
                lost_variables.append(variable)

        while lost_variables:
            del (self._propVariables[lost_variables.pop(0)])

        for variable in new_variables:
            self._propVariables[variable] = prop_variables[variable]

        self.rebuildWidgets.emit()
        self.accept()

    # __________________________________________________________________
    @pyqtSlot()
    def onCredentialsEdition(self):

        addr = self._addrInput.text().strip()
        user = self._userInput.text().strip()
        pasw = self._paswInput.text().strip()

        if pasw:
            r = list(map(lambda x: hex(256 - x)[2:], pasw.encode('utf-8')))
            pasw = ''.join(r)

        self._sshCredentials['addr'] = addr
        self._sshCredentials['user'] = user
        self._sshCredentials['pasw'] = pasw

        PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles, self._widgetVariables,
                                self._widgetImages, self._widgetButtons, self._widgetHiddens,
                                self._relaunchCommand, self._sshCredentials)

    # __________________________________________________________________
    @pyqtSlot()
    def onEdit(self):

        dlg = PanelWidgetsEditor(self._propVariables, self._propSettings,
                               self._widgetGroups, self._widgetTitles,
                               self._widgetVariables, self._widgetImages, self._widgetButtons,
                               self._widgetHiddens, self._relaunchCommand, self._sshCredentials, self._logger)
        dlg.setModal(True)

        dlg.rebuild.connect(self.rebuildWidgets)

        dlg.exec()


