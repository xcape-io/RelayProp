#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PinGroupButton.py
MIT License (c) Marie Faure <dev at faure dot systems>

Prop control push button.
"""

from PushButton import PushButton

from PyQt5.QtCore import pyqtSlot, Qt


class PinGroupButton(PushButton):

    # __________________________________________________________________
    def __init__(self, caption, action, topic):
        super(PinGroupButton, self).__init__(caption, action, topic)
