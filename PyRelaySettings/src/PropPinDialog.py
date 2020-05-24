#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PropPinDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Configure a prop pin.
"""

from constants import *
import re

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton, QMessageBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox
from PyQt5.QtGui import QIcon


class PropPinDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, pin_key, pin, pins_available, prop_pins, mega=False):

        super(PropPinDialog, self).__init__()

        self._key = pin_key
        self._pin = pin
        self._pinsAvailable = pins_available
        self._propPins = prop_pins
        self._mega = mega

        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)

        self.setStyleSheet("QDialog { border: 1px solid darkgrey }")

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        pin_layout = QGridLayout()
        pin_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(pin_layout)

        pin_layout.addWidget(QLabel(self.tr("<b>Output</b>")), pin_layout.rowCount(), 0, Qt.AlignHCenter)
        pin_layout.addWidget(QLabel(self.tr("<b>Variable</b>")) , pin_layout.rowCount() - 1, 1, Qt.AlignHCenter)
        pin_layout.addWidget(QLabel(self.tr("<b>Initial</b>")) , pin_layout.rowCount() - 1, 2, Qt.AlignHCenter)
        pin_layout.addWidget(QLabel(self.tr("<b>HIGH</b>")) , pin_layout.rowCount() - 1, 3, Qt.AlignHCenter)
        pin_layout.addWidget(QLabel(self.tr("<b>LOW</b>")) , pin_layout.rowCount() - 1, 4, Qt.AlignHCenter)

        self._pinSelection = QComboBox()
        for p in self._pinsAvailable:
            self._pinSelection.addItem(p)
        self._variableInput = QLineEdit()
        self._variableInput.setFixedWidth(VARIABLE_INPUT_WIDTH)
        self._initialSelection = QComboBox()
        self._initialSelection.addItem('LOW', 0)
        self._initialSelection.addItem('HIGH', 1)
        self._aliasHighInput = QLineEdit()
        self._aliasHighInput.setFixedWidth(ALIAS_INPUT_WIDTH)
        self._aliasLowInput = QLineEdit()
        self._aliasLowInput.setFixedWidth(ALIAS_INPUT_WIDTH)

        if self._mega:
            self._variableInput.setMaxLength(MEGA_VARIABLE_MAX_LENGTH)
            self._aliasHighInput.setMaxLength(MEGA_ALIAS_MAX_LENGTH)
            self._aliasLowInput.setMaxLength(MEGA_ALIAS_MAX_LENGTH)

        pin_layout.addWidget(self._pinSelection, pin_layout.rowCount(), 0)
        pin_layout.addWidget(self._variableInput , pin_layout.rowCount() - 1, 1, Qt.AlignHCenter)
        pin_layout.addWidget(self._initialSelection , pin_layout.rowCount() - 1, 2, Qt.AlignHCenter)
        pin_layout.addWidget(self._aliasHighInput , pin_layout.rowCount() - 1, 3, Qt.AlignHCenter)
        pin_layout.addWidget( self._aliasLowInput, pin_layout.rowCount() - 1, 4, Qt.AlignHCenter)

        i = self._pinSelection.findText(self._key)
        self._pinSelection.setCurrentIndex(i)

        self._variableInput.setText(self._pin.getVariable())

        i = self._initialSelection.findData(self._pin.getInitial())
        self._initialSelection.setCurrentIndex(i)

        alias_high, alias_low = self._pin.getAlias()
        self._aliasHighInput.setText(alias_high)
        self._aliasLowInput.setText(alias_low)

        apply_button = QPushButton(self.tr("Apply"))
        apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cancel_button = QPushButton(self.tr("Cancel"))
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_button.setFocusPolicy(Qt.NoFocus)

        delete_button = QPushButton(self.tr("Delete"))
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_button.setFocusPolicy(Qt.NoFocus)

        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        main_layout.addSpacing(4)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        apply_button.released.connect(self.onApply)
        cancel_button.released.connect(self.reject)
        delete_button.released.connect(self.onDelete)

    # __________________________________________________________________
    @pyqtSlot()
    def onApply(self):

        bad_chars = r'[\s=:*]'

        pin = self._pinSelection.currentText()
        variable = re.sub(bad_chars, '', self._variableInput.text().strip())

        if variable in ['board', 'settings', 'settings-date', 'rssi']:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('./x-settings.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText(self.tr("Variable '{}' is reserved to identify prop board and settings.".format(variable)))
            msg.setWindowTitle("Duplicate variable")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        initial = self._initialSelection.currentData()
        t = re.sub(bad_chars, '', self._aliasHighInput.text().strip())
        f = re.sub(bad_chars, '', self._aliasLowInput.text().strip())
        if not t:
            t = '1'
        if not f:
            f = '0'

        if self._mega:
            if len(variable.encode('utf-8')) + len(f.encode('utf-8')) + len(t.encode('utf-8')) > MEGA_TOTAL_MAX_LENGTH:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('./x-settings.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText(self.tr("Variable + HIGH + LOW total UTF-8 length exceeds {} bytes.".format(MEGA_TOTAL_MAX_LENGTH)))
                msg.setWindowTitle("Entries too long")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            elif len(variable.encode('utf-8')) > MEGA_VARIABLE_MAX_LENGTH:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('./x-settings.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText(self.tr("Variable '{}' is tool long due to UTF-8 encoding.".format(variable)))
                msg.setWindowTitle("Variable too long")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            elif len(t.encode('utf-8')) > MEGA_ALIAS_MAX_LENGTH:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('./x-settings.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText(self.tr("HIGH '{}' is tool long due to UTF-8 encoding.".format(t)))
                msg.setWindowTitle("HIGH too long")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            elif len(f.encode('utf-8')) > MEGA_ALIAS_MAX_LENGTH:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('./x-settings.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText(self.tr("LOW '{}' is tool long due to UTF-8 encoding.".format(f)))
                msg.setWindowTitle("LOW too long")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

        if variable:
            if pin is not None:
                for k, p in self._propPins.items():
                    if variable == p.getVariable() and k != pin and k != self._key:
                        msg = QMessageBox()
                        msg.setWindowIcon(QIcon('./x-settings.png'))
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText(self.tr("Variable '{}' already used by {}.".format(variable, k)))
                        msg.setWindowTitle("Duplicate variable")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.exec_()
                        return

        if variable:
            if pin != self._key:
                try:
                    self._propPins.pop(self._key)
                except:
                    pass  # sometimes it has already been removed (but I don't know why)
            self._pin.setPin(pin)
            self._pin.setVariable(variable)
            self._pin.setInitial(initial)
            self._pin.setAlias(t, f)
            self.accept()
        else:
            self._pin.setPin(pin)
            self.done(-1)

    # __________________________________________________________________
    @pyqtSlot()
    def onDelete(self):

        pin = self._pinSelection.currentText()
        self._pin.setPin(pin)
        self.done(-1)
