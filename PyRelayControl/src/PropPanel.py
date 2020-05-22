#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PropPanel.py
MIT License (c) Marie Faure <dev at faure dot systems>

Class to represent a prop panel.
"""
from constants import *
from PropPin import PropPin
import os
import json
import codecs
import configparser

class PropPanel:

    # __________________________________________________________________
    @classmethod
    def getJson(self, file, logger):

        prop_variables = {}
        if os.path.isfile(file):
            try:
                with open(file, 'r', encoding='utf-8') as fp:
                    json_list = json.load(fp)
                for p in json_list:
                    try:
                        key = p['pin']
                        if key is not None:
                            prop_variables[p['variable']] = PropPin(key, p['variable'], p['initial'], p['alias'])
                            logger.info("Variable loaded from JSON file : {}".format(p))
                    except Exception as e:
                        logger.warning("Failed load variable from JSON file : {}".format(p))
                        logger.warning(e)
            except json.JSONDecodeError as jex:
                logger.error("JSONDecodeError '{}' at {} in: {}".format(jex.msg, jex.pos, jex.doc))
            except Exception as e:
                logger.error("Failed to load JSON file '{0}'".format(file))
                logger.debug(e)
        return prop_variables
