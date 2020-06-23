#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PanelAdminModeDialog.py
MIT License (c) Faure Systems <dev at faure dot systems>

Dialog to enter admin password.
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtGui import QIcon


class PanelAdminModeDialog(QDialog):
    rebuildWidgets = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, admin_mode, prop_settings, logger):

        super(PanelAdminModeDialog, self).__init__()

        self._logger = logger
        self._adminMode = admin_mode  # mutable
        self._propSettings = prop_settings

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Admin mode"))

        self.setWindowIcon(QIcon('./x-relay.png'))

        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        pasw_layout = QHBoxLayout()
        main_layout.addLayout(pasw_layout)

        self._paswInput = QLineEdit()
        self._paswInput.setEchoMode(QLineEdit.Password)

        pasw_layout.addWidget(QLabel(self.tr("Password :")))
        pasw_layout.addWidget(self._paswInput)

        apply_button = QPushButton(self.tr("Apply"))
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cancel_button = QPushButton(self.tr("Ignore"))
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

        r = list(map(lambda x: chr(256 - int(x)), bytearray.fromhex(self._propSettings['options']['admin_password'])))
        password = ''.join(r)

        if password == self._paswInput.text().strip():
            self._adminMode.set(1)

        self.accept()

