#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EditPanelWidgets.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to edit caption and indicators.
"""

from constants import *
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QComboBox, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QFrame
from PyQt5.QtGui import QIcon


class EditPanelWidgets(QDialog):

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings, logger):

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables
        self._groupBoxes = {}

        super(EditPanelWidgets, self).__init__()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Edit captions and indicators"))

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.buildUi()

    # __________________________________________________________________
    def _buttonEditor(self, action, variable):

        ew = QWidget()
        layout = QHBoxLayout(ew)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        action_widget = QLineEdit(action)
        action_widget.setFrame(QFrame.NoFrame)
        action_widget.setReadOnly(True)
        caption_input = QLineEdit(variable.capitalize())

        layout.addWidget(QLabel(self.tr("Button")))
        layout.addWidget(action_widget)
        layout.addWidget(caption_input)

        return (ew, caption_input)

    # __________________________________________________________________
    def _groupEditor(self, group):

        ew = QWidget()
        layout = QHBoxLayout(ew)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if group is not None:
            action_widget = QLineEdit('{}/'.format(group))
            action_widget.setFrame(QFrame.NoFrame)
            action_widget.setReadOnly(True)
            caption_input = QLineEdit(group.capitalize())
        else:
            caption_input = QLineEdit()

        layout.addWidget(QLabel(self.tr("Group")))
        if group is not None:layout.addWidget(action_widget)
        layout.addWidget(caption_input)

        return (ew, caption_input)

    # __________________________________________________________________
    def _switchEditor(self, action, variable):

        ew = QWidget()
        layout = QHBoxLayout(ew)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        action_widget = QLineEdit(action)
        action_widget.setFrame(QFrame.NoFrame)
        action_widget.setReadOnly(True)
        label_input = QLineEdit(variable.capitalize())
        image_selector = QComboBox()

        image_selector.addItem(self.tr("Light"), 'light')
        image_selector.addItem(self.tr("Door"), 'door')
        image_selector.addItem(self.tr("Smoke"), 'smoke')
        image_selector.addItem(self.tr("Plug"), 'plug')
        image_selector.addItem(self.tr("Relay"), 'relay')

        layout.addWidget(QLabel(self.tr("Switch")))
        layout.addWidget(action_widget)
        layout.addWidget(label_input)
        layout.addWidget(image_selector)

        return (ew, label_input, image_selector)

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        for v, pin in self._propVariables.items():
            if '/' in v:
                group, variable = v.split('/', 1)
            else:
                group = None
                variable = v
            switch, label_input, image_selector = self._switchEditor(pin.getVariable(), variable)
            '''
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
            '''
            if group in self._groupBoxes:
                self._groupBoxes[group].layout().addWidget(switch)
            else:
                box = QGroupBox()
                box_layout = QVBoxLayout(box)
                box_layout.setSpacing(12)
                self._groupBoxes[group] = box
                main_layout.addWidget(box)
                box_layout.addWidget(switch)

        for group in list(self._groupBoxes.keys()):
            title, title_input = self._groupEditor(group)
            self._groupBoxes[group].layout().insertWidget(0, title)
            if group is None: continue
            button_on, button_on_input = self._buttonEditor('{}/*:{}'.format(group, str(GPIO_HIGH)), group)
            self._groupBoxes[group].layout().addWidget(button_on)

            button_off, button_off_input = self._buttonEditor('{}/*:{}'.format(group, str(GPIO_LOW)), group)
            self._groupBoxes[group].layout().addWidget(button_off)

        self.setLayout(main_layout)
