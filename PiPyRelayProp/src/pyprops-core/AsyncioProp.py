#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AsyncioProp.py
MIT License (c) Faure Systems <dev at faure dot systems>

Add asyncio periodic tasks handling to Props base class.
"""

from constants import *
from PropApp import PropApp
import asyncio


class AsyncioProp(PropApp):

    # __________________________________________________________________
    def __init__(self, argv, client, debugging_mqtt=False):
        super().__init__(argv, client, debugging_mqtt)

        self.addPeriodicAction("send all data", self._sendAllDataPeriodicTask, PUBLISHALLDATA_PERIOD)

    # __________________________________________________________________
    async def _sendAllDataPeriodicTask(self, period):
        while True:
            self.sendAllData()
            await asyncio.sleep(period)

    # __________________________________________________________________
    async def _sendDataChangesPeriodicTask(self, period):
        while True:
            self.sendDataChanges()
            await asyncio.sleep(period)

    # __________________________________________________________________
    def withEventLoop(self, loop):
        # Periodic actions
        for title, (func, time) in self._periodicActions.items():
            try:
                loop.create_task(func(time))
                self._logger.info("Periodic task created '{0}' every {1} seconds".format(title, time))
            except Exception as e:
                self._logger.error("Failed to create periodic task '{0}'".format(title))
                self._logger.debug(e)
