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

    # __________________________________________________________________
    @classmethod
    def getWidgets(self, logger):

        prop_widgets = {}
        ini = 'widgets.ini'
        if os.path.isfile(ini):
            self.config = configparser.ConfigParser()
            self.config.read_file(codecs.open(ini, 'r', 'utf8'))
            if "mqtt" in self.config.sections():
                for key in self.config.options("mqtt"):
                    self._definitions[key] = self.config.get("mqtt", key)
                    if key.startswith('mqtt-sub-'):
                        self._mqttSubscriptions.append(self._definitions[key])
                    if key == 'app-inbox':
                        self._mqttInbox = self._definitions[key]
                        self._mqttSubscriptions.append(self._mqttInbox)
                    if key == 'app-outbox':
                        self._mqttOutbox = self._definitions[key]

        return prop_widgets

'''
oid ControlPanelDialog::loadIniFile()
{
	QSettings dlg_settings(m_path, QSettings::IniFormat);
	dlg_settings.setIniCodec("UTF-8");

	m_title = dlg_settings.value(QLatin1String("dashboard")).toString();
	QString default_props = dlg_settings.value(QLatin1String("default-props")).toString();

	if (dlg_settings.childGroups().isEmpty())
	{
		QGroupBox *group = new QGroupBox(tr("Empty panel"), this);

		QVBoxLayout *vboxLayout = new QVBoxLayout(group);

		vboxLayout->setSpacing(2);
		vboxLayout->setSizeConstraint(QLayout::SetMinAndMaxSize);

		group->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Fixed);

		m_mainVLayout->addWidget(group);

		QPushButton *button = new QPushButton(tr("Configure panel"), this);

		vboxLayout->addWidget(button);

		connect(button, SIGNAL(clicked(bool)), SLOT(onConfigureClicked(bool)));

		QTimer::singleShot(0, this, SLOT(shrink()));

		return;
	}

	Props *props_by_default = m_roomInfo->props(default_props);

	if (props_by_default) m_propses << props_by_default;

	for each (QString group_index in dlg_settings.childGroups())
	{
		dlg_settings.beginGroup(group_index);

		//qDebug() << "Group" << group_index << dlg_settings.value("title").toString();

		QGroupBox *group = new QGroupBox(dlg_settings.value("title").toString(), this);
		group->setStyleSheet(QString("QGroupBox {%1}").arg(dlg_settings.value(QLatin1String("style")).toString())); 

		QVBoxLayout *vboxLayout = new QVBoxLayout(group);

		vboxLayout->setSpacing(2);
		vboxLayout->setSizeConstraint(QLayout::SetMinAndMaxSize);

		group->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Fixed);

		m_mainVLayout->addWidget(group);

		if (dlg_settings.value("type").toString() == "select") // Select
		{
			//qDebug() << "Select" << group_index << dlg_settings.value("title").toString();

			group->setTitle(dlg_settings.value("title").toString());
			group->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Fixed);

			QMultiMap<QString, QString> options;

			for each (QString opt in dlg_settings.childKeys())
			{
				options.replace(opt, dlg_settings.value(opt).toString());
			}

			for each (QString item_index in dlg_settings.childGroups())
			{
				dlg_settings.beginGroup(item_index);

				QString item_string = QString("%1\n%2\n%3").arg(dlg_settings.value("item").toString()).arg(dlg_settings.value("detail").toString()).arg(dlg_settings.value("request").toString());

				options.insertMulti("items", item_string);

				dlg_settings.endGroup();
			}

			ControlPanelWidget *widget = new ControlPanelWidget(dlg_settings.value("type").toString(), -1, options, m_title, m_roomInfo, group);

			m_controlPanelWidgets << widget;

			connect(widget, SIGNAL(actuator(QString, QString, Rc::Actuator)), SIGNAL(actuator(QString, QString, Rc::Actuator)), Qt::QueuedConnection);
			connect(widget, SIGNAL(program(QString)), SIGNAL(program(QString)), Qt::QueuedConnection);

			widget->setContentsMargins(0, 0, 0, 0);

			vboxLayout->addWidget(widget);

			if (options.value("user") == "0") m_adminWidgets << widget;

			Props *props = m_roomInfo->props(options.value("props"));
			if (!props) props = props_by_default;

			if (props)
			{
				if (!m_propses.contains(props)) m_propses << props;

				if (!m_controlPanelWidgetFromChannel.contains(props->channel()))
				{
					m_mqttSubtopics << props->channel();
					m_controlPanelWidgetFromChannel[props->channel()] = QMultiHash<QString, ControlPanelWidget*>();
				}

				if (!options.value("variable").isEmpty())
					m_controlPanelWidgetFromChannel[props->channel()].insertMulti(options.value("variable"), widget);

				if (!options.value("extension").isEmpty())
					m_controlPanelWidgetFromChannel[props->channel()].insertMulti(options.value("extension"), widget);

				if (options.value("variable").isEmpty() && options.value("extension").isEmpty())
					m_controlPanelWidgetFromChannel[props->channel()].insertMulti(QString(), widget);
			}
		}
		else
		{
			int caption_width = dlg_settings.value(QLatin1String("caption-width"), -1).toInt();

			for each (QString g in dlg_settings.childGroups())
			{
				dlg_settings.beginGroup(g);

				//qDebug() << "Widget" << g << dlg_settings.value("label").toString();

				QMultiMap<QString, QString> options;

				for each (QString opt in dlg_settings.childKeys())
				{
					//qDebug() << "Widget" << g << dlg_settings.value("label").toString() << opt << dlg_settings.value(opt).toString();

					options.replace(opt, dlg_settings.value(opt).toString());
				}

				ControlPanelWidget *widget = new ControlPanelWidget(dlg_settings.value("type").toString(), caption_width, options, m_title, m_roomInfo, this);

				m_controlPanelWidgets << widget;

				connect(widget, SIGNAL(actuator(QString, QString, Rc::Actuator)), SIGNAL(actuator(QString, QString, Rc::Actuator)), Qt::QueuedConnection);
				connect(widget, SIGNAL(program(QString)), SIGNAL(program(QString)), Qt::QueuedConnection);

				widget->setContentsMargins(0, 0, 0, 0);

				vboxLayout->addWidget(widget);

				if (options.value("user") == "0") m_adminWidgets << widget;

				Props *props = m_roomInfo->props(options.value("props"));
				if (!props) props = props_by_default;

				if (props)
				{
					if (!m_propses.contains(props)) m_propses << props;

					if (!m_controlPanelWidgetFromChannel.contains(props->channel()))
					{
						m_mqttSubtopics << props->channel();
						m_controlPanelWidgetFromChannel[props->channel()] = QMultiHash<QString, ControlPanelWidget*>();
					}

					if (!options.value("variable").isEmpty())
						m_controlPanelWidgetFromChannel[props->channel()].insertMulti(options.value("variable"), widget);

					if (!options.value("extension").isEmpty())
						m_controlPanelWidgetFromChannel[props->channel()].insertMulti(options.value("extension"), widget);

					if (options.value("variable").isEmpty() && options.value("extension").isEmpty())
						m_controlPanelWidgetFromChannel[props->channel()].insertMulti(QString(), widget);
				}

				dlg_settings.endGroup();
			}
		}

		dlg_settings.endGroup();
	}

	QTimer::singleShot(0, this, SLOT(shrink()));
}
'''