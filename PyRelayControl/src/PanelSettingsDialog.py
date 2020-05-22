#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PanelSettingsDialog.py
MIT License (c) Marie Faure <dev at faure dot systems>

Dialog to configure control parameters.
"""

from HelpDialog import HelpDialog
from PropPanel import PropPanel

from PyQt5.QtCore import Qt, pyqtSlot, QDir, QFileInfo, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import QDialog, QPushButton, QGroupBox
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
import os
import json

class PanelSettingsDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, prop_variables, prop_settings, logger):

        super(PanelSettingsDialog, self).__init__()

        self._logger = logger
        self._propSettings = prop_settings
        self._propVariables = prop_variables

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr("Panel configuration"))

        self.setWindowIcon(QIcon('./images/cog-black.svg'))

        self.setMinimumWidth(400)
        self.buildUi()

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        settings_box = QGroupBox(self.tr("Prop settings"))
        settings_box_layout = QVBoxLayout(settings_box)
        main_layout.addWidget(settings_box)

        json_layout = QHBoxLayout()
        settings_box_layout.addLayout(json_layout)

        self._jsonInput = QLineEdit()
        self._jsonInput.setDisabled(True)

        json_browse_button = QPushButton()
        json_browse_button.setIcon(QIcon('./images/folder.svg'))
        json_browse_button.setFlat(True)
        json_browse_button.setToolTip(self.tr("Browse to select JSON file"))
        json_browse_button.setIconSize(QSize(16, 16))
        json_browse_button.setFixedSize(QSize(20, 20))

        json_layout.addWidget(QLabel("JSON file"))
        json_layout.addWidget(self._jsonInput)
        json_layout.addWidget(json_browse_button)

        add_button = QPushButton(" {} ".format(self.tr("Add widgets from new settings")))
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_box_layout.addWidget(add_button)

        self._settingsWidget = QWidget()
        self._settingsWidget.setContentsMargins(0, 0, 0, 0)
        settings_layout = QGridLayout(self._settingsWidget)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._settingsWidget)

        prop_name_label = QLabel(self.tr("Prop name"))
        settings_layout.addWidget(prop_name_label, settings_layout.rowCount(), 0)
        self._propNameInput = QLineEdit()
        settings_layout.addWidget(self._propNameInput, settings_layout.rowCount() - 1, 1)

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

        apply_button.pressed.connect(self.onApply)
        cancel_button.pressed.connect(self.accept)
        help_button.pressed.connect(self.onHelp)
        add_button.pressed.connect(self.onAdd)
        json_browse_button.pressed.connect(self.onBrowse)

        if 'prop' in self._propSettings and 'json' in self._propSettings['prop']:
            self._jsonInput.setText(os.path.basename(self._propSettings['prop']['json']))

    # __________________________________________________________________
    @pyqtSlot()
    def onAdd(self):

        if 'prop' in self._propSettings and 'json' in self._propSettings['prop']:
            prop_variables = PropPanel.getJson(self._propSettings['prop']['json'], self._logger)
        else:
            msg = QMessageBox()
            msg.setWindowIcon(self.windowIcon())
            msg.setIcon(QMessageBox.Warning)
            msg.setText(self.tr("There is no JSON file from prop settings, select one."))
            msg.setWindowTitle("Missing JSON")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        new_variables = []
        for variable in prop_variables:
            if variable not in self._propVariables:
                new_variables.append(variable)

        lost_variables = []
        for variable in self._propVariables:
            if variable not in prop_variables:
                lost_variables.append(variable)

        while lost_variables:
            variable = lost_variables.pop(0)
            if variable in self._propVariables:
                msg = QMessageBox()
                msg.setWindowIcon(self.windowIcon())
                msg.setIcon(QMessageBox.Question)
                msg.setText(self.tr("The variable '{}' at {} is no longer in the prop pins.").format(variable,
                            self._propVariables[variable].getPin()) +
                            "<br><br>" +
                            self.tr("Do you want to keep its widget in the panel?"))
                msg.setWindowTitle("Deprecated variable")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No |
                                       QMessageBox.YesToAll| QMessageBox.NoToAll)
                msg.setDefaultButton(QMessageBox.No)
                res = msg.exec_()
                if res == QMessageBox.Yes:
                    del(self._propVariables[variable])
                elif res == QMessageBox.YesToAll:
                    while lost_variables:
                        del(self._propVariables[lost_variables.pop(0)])
                    break
                elif res == QMessageBox.NoToAll:
                    break

        if not new_variables:
            msg = QMessageBox()
            msg.setWindowIcon(self.windowIcon())
            msg.setIcon(QMessageBox.Information)
            msg.setText(self.tr("There is no new variable in the prop pins."))
            msg.setWindowTitle("Loading variables")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            for variable in new_variables:
                self._propVariables[variable] = prop_variables[variable]
            msg = QMessageBox()
            msg.setWindowIcon(self.windowIcon())
            msg.setIcon(QMessageBox.Information)
            if len(new_variables) == 1:
                msg.setText(self.tr("Loaded 1 new variables for the prop pins."))
            else:
                msg.setText(self.tr("Loaded {} new variables for the prop pins.").format(len(new_variables)))
            msg.setWindowTitle("Loading variables")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        return

    # __________________________________________________________________
    @pyqtSlot()
    def onApply(self):

        pass

        #with open('settins.ini', 'w') as configfile:
        #    self._propSettings.write(configfile)

        self.accept()

    # __________________________________________________________________
    @pyqtSlot()
    def onBrowse(self):

        if 'prop' in self._propSettings and 'json' in self._propSettings['prop']:
            json_path = self._propSettings['prop']['json']
            json_dir = os.path.dirname(json_path)
        else:
            json_path = None
            json_dir = os.getcwd()

        dlg = QFileDialog(self,
                          self.tr("Select prop settings JSON file"),
                          json_dir,
                          self.tr("JSON files (*.json);; All files (*.*)"))

        dlg.setViewMode(QFileDialog.Detail)
        dlg.setFileMode(QFileDialog.ExistingFile)

        if json_path:
            dlg.selectFile(os.path.basename(json_path))

        ret = dlg.exec()

        if QDialog.Accepted == ret and len(dlg.selectedFiles()) == 1:
            returned_path = dlg.selectedFiles()[0]

            if os.path.isfile(returned_path):
                self._propSettings['prop']['json'] = returned_path
                self._jsonInput.setText(os.path.basename(returned_path))
                with open('prop.ini', 'w') as configfile:
                    self._propSettings.write(configfile)

    # __________________________________________________________________
    @pyqtSlot()
    def onHelp(self):

        dlg = HelpDialog(self.tr("Edit the control panel"), './help/panel.html')
        dlg.exec()
