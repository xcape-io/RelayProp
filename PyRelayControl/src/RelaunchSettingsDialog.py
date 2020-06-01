#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RelaunchSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure SSH command to relaunch the prop.
"""

from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5.QtWidgets import QLabel, QTextEdit
from PyQt5.QtGui import QIcon


class RelaunchSettingsDialog(QDialog):
    rebuildWidgets = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, title, relaunch_command, prop_settings, logger):

        super(RelaunchSettingsDialog, self).__init__()

        self._logger = logger
        self._propSettings = prop_settings
        self._relaunchCommand = relaunch_command

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.setMinimumWidth(400)
        self.buildUi()

        if 'board' in self._propSettings['prop'] and self._propSettings['prop']['board'] == 'mega':
            if 'mega_bridge' in self._propSettings['prop'] and self._propSettings['prop']['mega_bridge'] == '1':
                ssh = "echo %BROKER%> /root/broker && reset-mcu"
            else:
                self._logger.warning("Relaunch ignored : {}".format('ssh not supported for this board'))
                return
        else:
            if 'command' in self._relaunchCommand:
                ssh = self._relaunchCommand['command']
            else:
                ssh = "ps aux | grep python | grep -v \"grep python\" | grep PiPyRelayProp/src/main.py | awk '{print $2}' | xargs kill -9 && screen -d -m python3 /home/pi/Room/Props/PiPyRelayProp/src/main.py -s %BROKER%"

        self._sshInput.setText(ssh)

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        ssh_layout = QHBoxLayout()
        main_layout.addLayout(ssh_layout)

        self._sshInput = QTextEdit()
        self._sshInput.setAlignment(Qt.AlignTop)
        self._sshInput.setFixedHeight(76)

        ssh_layout.addWidget(QLabel(self.tr("SSH command")), 0, Qt.AlignTop)
        ssh_layout.addWidget(self._sshInput)

        apply_button = QPushButton(self.tr("Apply"))
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cancel_button = QPushButton(self.tr("Cancel"))
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        cancel_button.released.connect(self.reject)
        apply_button.released.connect(self.onApply)

    # __________________________________________________________________
    @pyqtSlot()
    def onApply(self):

        ssh = self._sshInput.toPlainText().strip()

        self._relaunchCommand['command'] = ssh

        self.accept()