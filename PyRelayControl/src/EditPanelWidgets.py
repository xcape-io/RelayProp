#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EditPanelWidgets.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to edit caption and indicators.
"""

from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
import os


class EditPanelWidgets(QDialog):

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings, logger):

        super(EditPanelWidgets, self).__init__()

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Edit captions and indicators"))

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)



        self.setLayout(main_layout)
