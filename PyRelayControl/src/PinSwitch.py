#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PinSwitch.py
MIT License (c) Marie Faure <dev at faure dot systems>

Prop switch widget.
"""

from SwitchWidget import SwitchWidget

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon

import os


class PinSwitch(SwitchWidget):

    # __________________________________________________________________
    def __init__(self,
                 label,
                 variable,
                 image_on,
                 image_off,
                 sync,
                 sync_on,
                 sync_off,
                 action_on,
                 action_off,
                 topic,
                 value_on='1',
                 value_off='0',
                 label_width=0):

        super(PinSwitch, self).__init__(label, variable, image_on, image_off,
                                        sync, sync_on, sync_off, action_on, action_off, topic,
                                        value_on, value_off)

