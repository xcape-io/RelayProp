#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EditPanelWidgets.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to edit caption and indicators.
"""

from constants import *
from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QComboBox, QGroupBox, QPushButton
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QFrame
from PyQt5.QtGui import QIcon


class EditPanelWidgets(QDialog):
    rebuild = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings,
                 widget_groups, widget_titles, widget_variables, logger):

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables
        self._groupBoxes = {}
        self._widgetGroups = widget_groups
        self._widgetTitles = widget_titles
        self._widgetVariables = widget_variables

        self._imageSelections = {}
        self._labelInputs = {}
        self._titleInputs = {}
        self._moveUpButtons = {}
        self._moveDownButtons = {}

        super(EditPanelWidgets, self).__init__()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Edit captions and indicators"))

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.buildUi()

        self.rebuild.connect(self.rebuildGroups)

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

        move_up_button = QPushButton()
        move_up_button.setFlat(True)
        move_up_button.setToolTip(self.tr("Move group up"))
        move_up_button.setIconSize(QSize(10, 10))
        move_up_button.setFixedSize(QSize(14, 14))
        move_up_button.setIcon(QIcon('./images/caret-top'))

        move_down_button = QPushButton()
        move_down_button.setFlat(True)
        move_down_button.setToolTip(self.tr("Move group down"))
        move_down_button.setIconSize(QSize(20, 20))
        move_down_button.setFixedSize(QSize(28, 28))
        move_down_button.setIcon(QIcon('./images/caret-bottom'))

        layout.addWidget(move_up_button)
        layout.addWidget(move_down_button)

        return (ew, caption_input, move_up_button, move_down_button)

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

        self.setLayout(main_layout)

        self.rebuildGroups()

    # __________________________________________________________________
    @pyqtSlot()
    def onImageSelection(self):

        combobox = self.sender()
        if combobox not in self._imageSelections:
            self._logger.warning("Image selection not found")
            return

        variable = self._imageSelections[combobox]
        pass

    # __________________________________________________________________
    @pyqtSlot()
    def onLabelEdition(self):

        input = self.sender()
        if input not in self._labelInputs:
            self._logger.warning("Label input not found")
            return

        variable = self._labelInputs[input]
        pass

    # __________________________________________________________________
    @pyqtSlot()
    def onMoveGroupDown(self):

        button = self.sender()
        if button not in self._moveDownButtons:
            self._logger.warning("Button not found : {}".format(button.toolTip()))
            return

        group = self._moveDownButtons[button]

        try:
            i = self._widgetGroups.index(group)
        except ValueError:
            return

        if i < len(self._widgetGroups) - 1:
            self._widgetGroups.pop(i)
            self._widgetGroups.insert(i+1, group)
            self.rebuild.emit()
            PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles, self._widgetVariables)

    # __________________________________________________________________
    @pyqtSlot()
    def onMoveGroupUp(self):

        button = self.sender()
        if button not in self._moveUpButtons:
            self._logger.warning("Button not found : {}".format(button.toolTip()))
            return

        group = self._moveUpButtons[button]

        try:
            i = self._widgetGroups.index(group)
        except ValueError:
            return

        if i > 0:
            self._widgetGroups.pop(i)
            self._widgetGroups.insert(i-1, group)
            self.rebuild.emit()
            PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles, self._widgetVariables)


    # __________________________________________________________________
    @pyqtSlot()
    def onTitleEdition(self):

        input = self.sender()
        if input not in self._titleInputs:
            self._logger.warning("Title input not found")
            return

        variable = self._titleInputs[input]
        pass

    # __________________________________________________________________
    @pyqtSlot()
    def rebuildGroups(self):

        main_layout = self.layout()

        for group in list(self._groupBoxes.keys()):
            widgets = self._groupBoxes[group].findChildren(QWidget, '', options=Qt.FindChildrenRecursively)
            for w in widgets:
                try:
                    self._groupBoxes[group].layout().removeWidget(w)
                    w.deleteLater()
                except Exception as e:
                    print(e)
            del (widgets)
            main_layout.removeWidget(self._groupBoxes[group])
            self._groupBoxes[group].deleteLater()
            del (self._groupBoxes[group])

        for group in self._widgetGroups:
            box = QGroupBox()
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(12)
            self._groupBoxes[group] = box
            main_layout.addWidget(box)

        for v, pin in self._propVariables.items():
            if '/' in v:
                group, variable = v.split('/', 1)
            else:
                group = None
                variable = v
            switch, label_input, image_selector = self._switchEditor(pin.getVariable(), variable)
            self._labelInputs[label_input] = variable
            self._imageSelections[image_selector] = variable
            label_input.editingFinished.connect(self.onLabelEdition)
            image_selector.currentIndexChanged.connect(self.onImageSelection)

            if group in self._groupBoxes:
                self._groupBoxes[group].layout().addWidget(switch)
            else:
                box = QGroupBox()
                box_layout = QVBoxLayout(box)
                box_layout.setSpacing(12)
                self._groupBoxes[group] = box
                main_layout.addWidget(box)
                box_layout.addWidget(switch)
                self._widgetGroups.append(group)

        for group in list(self._groupBoxes.keys()):
            title, title_input, move_up_button, move_down_button = self._groupEditor(group)
            self._groupBoxes[group].layout().insertWidget(0, title)

            self._titleInputs[title_input] = group + '/' if group is not None else None
            self._moveUpButtons[move_up_button] = group
            self._moveDownButtons[move_down_button] = group

            title_input.editingFinished.connect(self.onTitleEdition)
            move_up_button.released.connect(self.onMoveGroupUp)
            move_down_button.released.connect(self.onMoveGroupDown)

            if group is None: continue

            button_on, button_on_input = self._buttonEditor('{}/*:{}'.format(group, str(GPIO_HIGH)), group)
            self._groupBoxes[group].layout().addWidget(button_on)

            button_off, button_off_input = self._buttonEditor('{}/*:{}'.format(group, str(GPIO_LOW)), group)
            self._groupBoxes[group].layout().addWidget(button_off)
