#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RelaunchSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure SSH command to relaunch the prop.
"""

from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
import os


class RelaunchSettingsDialog(QDialog):
    rebuildWidgets = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, title, ssh, logger):

        super(RelaunchSettingsDialog, self).__init__()

        self._logger = logger
        self._sshCommand = ssh

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        ssh_layout = QHBoxLayout()
        main_layout.addLayout(ssh_layout)

        self._sshInput = QLineEdit()
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

        cancel_button.released.connect(self.accept)
        apply_button.released.connect(self.onApply)

    # __________________________________________________________________
    @pyqtSlot()
    def onApply(self):

        pass
