#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PinGroupButton.py
MIT License (c) Faure Systems <dev at faure dot systems>

Prop control push button.
"""

from PushButton import PushButton


class PinGroupButton(PushButton):

    # __________________________________________________________________
    def __init__(self, group, level, topic):

        command = "ON" if level else "OFF"
        caption = '{} {}'.format(group.capitalize(), command)
        action = '{}/*:{}'.format(group, str(level))

        super(PinGroupButton, self).__init__(caption, action, topic)

