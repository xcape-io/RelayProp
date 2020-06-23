#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PropPin.py
MIT License (c) Faure Systems <dev at faure dot systems>

Class to represent a prop pin.
"""
from constants import *


class PropPin:

    # __________________________________________________________________
    def __init__(self, pin=None, variable='', initial=GPIO_LOW, alias=("1", "0"), logger=None):
        super().__init__()

        self._logger = logger
        self._pin = pin
        self._variable = variable
        self._initial = initial
        self._alias = alias

    # __________________________________________________________________
    def __str__(self):
        return "{}: variable='{}' initial='{}' values=('{}', '{}')".format(self._pin,
                                                                     self._variable, self._initial,
                                                                     self._alias[0], self._alias[1])

    # __________________________________________________________________
    def getAlias(self):
        return self._alias

    # __________________________________________________________________
    def getInitial(self):
        return self._initial

    # __________________________________________________________________
    def getPin(self):
        return self._pin

    # __________________________________________________________________
    def getVariable(self):
        return self._variable

    # __________________________________________________________________
    def isNull(self):
        return self._pin is None

    # __________________________________________________________________
    def setAlias(self, t, f):
        self._alias = (t, f)

    # __________________________________________________________________
    def setInitial(self, v):
        self._initial = v

    # __________________________________________________________________
    def setPin(self, v):
        self._pin = v

    # __________________________________________________________________
    def setVariable(self, v):
        self._variable = v

    # __________________________________________________________________
    def toJson(self):
        if self._pin is None:
            return "null"

        return "{" + "'pin': '{}', 'variable': '{}', initial: '{}', 'alias': ['{}', '{}']".format(self._pin,
                                                                                                  self._variable,
                                                                                                  self._initial,
                                                                                                  self._alias[0],
                                                                                                  self._alias[1]) + "}"
