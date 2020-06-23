#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HelpDialog.py
MIT License (c) Faure Systems <dev at faure dot systems>

Dialog to display HTML help file.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy, QStyle
from PyQt5.QtWidgets import QDialog, QTextBrowser, QPushButton, QFrame


class HelpDialog(QDialog):

    # __________________________________________________________________
    def __init__(self, title, file):

        super(HelpDialog, self).__init__()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)

        self.setWindowIcon(QIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion)))

        self.buildUi()

        with open('./help/help.css', 'r', encoding='utf8') as cssfile:
            css = cssfile.read()

        with open(file, 'r', encoding='utf8') as helpfile:
            help = helpfile.read()
            help = "<style>{}></style>\n\n<body>{}</body>".format(css, help)
            self._browser.setHtml(help)

        self.resize(480, 380)

    # __________________________________________________________________
    def buildUi(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        self._browser = QTextBrowser()
        self._browser.setReadOnly(True)
        self._browser.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(self._browser)

        close_button = QPushButton(self.tr("Close"))
        close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        close_button.released.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

