#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EditPanelWidgets.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to edit caption and indicators.
"""

from constants import *
from PropPanel import PropPanel
from SshSettingsDialog import SshSettingsDialog

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QComboBox, QGroupBox, QPushButton
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QFrame
from PyQt5.QtGui import QIcon


class EditPanelWidgets(QDialog):
    rebuild = pyqtSignal()
    reorder = pyqtSignal()

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings,
                 widget_groups, widget_titles,
                 widget_variables, widget_images, widget_buttons,
                 relaunch, logger):

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables
        self._groupBoxes = {}
        self._widgetGroups = widget_groups
        self._widgetTitles = widget_titles
        self._widgetVariables = widget_variables
        self._widgetImages = widget_images
        self._widgetButtons = widget_buttons
        self._relaunchCommand = relaunch

        self._imageSelections = {}
        self._labelInputs = {}
        self._titleInputs = {}
        self._moveUpButtons = {}
        self._moveDownButtons = {}
        self._groupButtons = {}

        self._propBox = None

        super(EditPanelWidgets, self).__init__()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Edit captions and indicators"))

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.buildUi()

        self.reorder.connect(self.buildGroups)

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
    @pyqtSlot()
    def buildGroups(self):

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

        if self._propBox is not None:
            widgets = self._propBox.findChildren(QWidget, '', options=Qt.FindChildrenRecursively)
            for w in widgets:
                try:
                    self._propBox.layout().removeWidget(w)
                    w.deleteLater()
                except Exception as e:
                    print(e)
            del (widgets)
            main_layout.removeWidget(self._propBox)
            self._propBox.deleteLater()
            del (self._propBox)

        top_group = None
        bottom_group = None

        for group in self._widgetGroups:
            if top_group is None:
                top_group = group
            bottom_group = group
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
            self._labelInputs[label_input] = v
            self._imageSelections[image_selector] = v
            if v in self._widgetVariables:
                label_input.setText(self._widgetVariables[v])
            if v in self._widgetImages:
                idx = image_selector.findData(self._widgetImages[v])
                if idx > 0:
                    image_selector.setCurrentIndex(idx)
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

            if group == top_group:
                move_up_button.setEnabled(False)
                move_up_button.setToolTip('')
            if group == bottom_group:
                move_down_button.setEnabled(False)
                move_down_button.setToolTip('')

            self._titleInputs[title_input] = group + '/' if group is not None else None
            self._moveUpButtons[move_up_button] = group
            self._moveDownButtons[move_down_button] = group

            title_input.editingFinished.connect(self.onTitleEdition)
            move_up_button.released.connect(self.onMoveGroupUp)
            move_down_button.released.connect(self.onMoveGroupDown)

            variable = group + '/' if group is not None else ''
            if variable in self._widgetTitles:
                title_input.setText(self._widgetTitles[variable])

            if group is None: continue

            v_high = '{}/*:{}'.format(group, str(GPIO_HIGH))
            button_on, button_on_input = self._buttonEditor(v_high, group)
            self._groupBoxes[group].layout().addWidget(button_on)

            v_low = '{}/*:{}'.format(group, str(GPIO_LOW))
            button_off, button_off_input = self._buttonEditor(v_low, group)
            self._groupBoxes[group].layout().addWidget(button_off)

            if v_high in self._widgetButtons:
                button_on_input.setText(self._widgetButtons[v_high])
            if v_low in self._widgetButtons:
                button_off_input.setText(self._widgetButtons[v_low])

            button_on_input.editingFinished.connect(self.onButtonEdition)
            button_off_input.editingFinished.connect(self.onButtonEdition)

            self._groupButtons[button_on_input] = v_high
            self._groupButtons[button_off_input] = v_low

            if v_high in self._widgetButtons:
                button_on_input.setText(self._widgetButtons[v_high])
            if v_low in self._widgetButtons:
                button_off_input.setText(self._widgetButtons[v_low])

        self._propBox = QGroupBox(self.tr("Prop board control"))
        box_layout = QVBoxLayout(self._propBox)
        box_layout.setSpacing(12)
        main_layout.addWidget(self._propBox)
        relaunch_button = QPushButton(self.tr("Relaunch"))
        reboot_button = QPushButton(self.tr("Reboot"))
        box_layout.addWidget(relaunch_button)
        box_layout.addWidget(reboot_button)

        relaunch_button.released.connect(self.onRelaunch)
        reboot_button.released.connect(self.onReboot)

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        self.setLayout(main_layout)

        self.buildGroups()

    # __________________________________________________________________
    @pyqtSlot()
    def onButtonEdition(self):

        input = self.sender()
        if input not in self._groupButtons:
            self._logger.warning("Label input not found")
            return

        variable = self._groupButtons[input]
        self._widgetButtons[variable] = input.text().strip()
        PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                self._widgetVariables, self._widgetImages, self._widgetButtons)
        self.rebuild.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onImageSelection(self):

        combobox = self.sender()
        if combobox not in self._imageSelections:
            self._logger.warning("Image selection not found")
            return

        variable = self._imageSelections[combobox]
        self._widgetImages[variable] = combobox.currentData()
        PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                self._widgetVariables, self._widgetImages, self._widgetButtons)
        self.rebuild.emit()

    # __________________________________________________________________
    @pyqtSlot()
    def onLabelEdition(self):

        input = self.sender()
        if input not in self._labelInputs:
            self._logger.warning("Label input not found")
            return

        variable = self._labelInputs[input]
        self._widgetVariables[variable] = input.text().strip()
        PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                self._widgetVariables, self._widgetImages, self._widgetButtons)
        self.rebuild.emit()

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
            PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                    self._widgetVariables, self._widgetImages, self._widgetButtons)
            self.rebuild.emit()
            self.reorder.emit()

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
            self.reorder.emit()
            PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                    self._widgetVariables, self._widgetImages, self._widgetButtons)

    # __________________________________________________________________
    @pyqtSlot()
    def onRelaunch(self):

        ssh = 'ahah'

        dlg = SshSettingsDialog(self.tr("Relaunch command"), ssh, self._logger)
        dlg.setModal(True)

        #dlg.rebuildWidgets.connect(self._buildPropWidgets)

        dlg.exec()

    # __________________________________________________________________
    @pyqtSlot()
    def onReboot(self):

        button = self.sender()

    # __________________________________________________________________
    @pyqtSlot()
    def onTitleEdition(self):

        input = self.sender()
        if input not in self._titleInputs:
            self._logger.warning("Title input not found")
            return

        variable = self._titleInputs[input]
        if variable is None: variable = ''
        self._widgetTitles[variable] = input.text().strip()
        self.rebuild.emit()
        PropPanel.savePanelJson(self._widgetGroups, self._widgetTitles,
                                self._widgetVariables, self._widgetImages, self._widgetButtons)

