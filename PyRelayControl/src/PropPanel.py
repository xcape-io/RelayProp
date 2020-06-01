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


class PropPanel:

    # __________________________________________________________________
    @classmethod
    def getVariablesJson(self, file, logger):

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

    # __________________________________________________________________
    @classmethod
    def loadPanelJson(self, logger):

        groups = []
        titles = {}
        variables = {}
        images = {}
        buttons = {}
        hiddens = {}
        relaunch = {}  # must be mutable
        credentials = {}
        if os.path.isfile('panel.json'):
            try:
                with open('panel.json', 'r', encoding='utf-8') as fp:
                    json_doc = json.load(fp)
                groups = json_doc['groups']
                titles = json_doc['titles']
                variables = json_doc['variables']
                images = json_doc['images']
                buttons = json_doc['buttons']
                hiddens = json_doc['hiddens']
                relaunch = json_doc['relaunch']
                credentials = json_doc['credentials']
            except json.JSONDecodeError as jex:
                logger.error("JSONDecodeError '{}' at {} in: {}".format(jex.msg, jex.pos, jex.doc))
            except Exception as e:
                logger.error("Failed to load JSON file 'panel.json'")
                logger.debug(e)
        return groups, titles, variables, images, buttons, hiddens, relaunch, credentials

    # __________________________________________________________________
    @classmethod
    def savePanelJson(self, groups, titles, variables, images, buttons, hiddens, relaunch, credentials):

        doc = {}
        doc['groups'] = groups
        doc['titles'] = titles
        doc['variables'] = variables
        doc['images'] = images
        doc['buttons'] = buttons
        doc['hiddens'] = hiddens
        doc['relaunch'] = relaunch
        doc['credentials'] = credentials

        with open('panel.json', 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(doc, indent=2, ensure_ascii=False))  # for UTF-8 encoding
