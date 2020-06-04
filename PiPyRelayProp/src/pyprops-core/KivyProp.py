#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
KivyProp.py

Base class for Kivy application with MQTT inbox/outbox.
'''

from constants import *

from kivy.app import App
from kivy.uix.button import Button

import configparser, codecs, yaml
import logging, logging.config
import argparse
import os
		
class KivyProp(App):

	#__________________________________________________________________
	def __init__(self, client, debugging_mqtt=False, **kwargs):

		super(KivyProp, self).__init__(**kwargs)
		
		self._config = {}
		self._definitions = {}
		self._mqttSubscriptions = []
		self._mqttInbox = None
		self._mqttOutbox = None
		self._mqttServerHost = MQTT_DEFAULT_HOST
		self._mqttServerPort = MQTT_DEFAULT_PORT

		ini = 'definitions.ini'
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

		if os.path.isfile(CONFIG_FILE):
			with open(CONFIG_FILE, 'r') as conffile:
				self._config = yaml.load(conffile, Loader=yaml.SafeLoader)
		else:
			self._config = {}
		
		print('Config:', self._config)
		
		self._mqttClient = client
		self._mqttConnected = False
		if 'host' in self._config: 
			self._mqttServerHost = self._config['host'] 
		if 'port' in self._config: 
			self._mqttServerPort = self._config['port'] 

		self._mqttClient.on_connect = self._mqttOnConnect
		self._mqttClient.on_disconnect = self._mqttOnDisconnect
		self._mqttClient.on_message = self._mqttOnMessage
		self._mqttClient.on_publish = self._mqttOnPublish
		self._mqttClient.on_subscribe = self._mqttOnSubscribe
		self._mqttClient.on_unsubscribe = self._mqttOnUnsubscribe
		
		if debugging_mqtt:		
			self._mqttClient.on_log = self._mqttOnLog

		parser = argparse.ArgumentParser()
		parser.add_argument("-s", "--server", help="change MQTT server host", nargs=1)
		parser.add_argument("-p", "--port", help="change MQTT server port", nargs=1, type=int)
		parser.add_argument("-d", "--debug", help="set DEBUG log level", action='store_true')
		parser.add_argument("-l", "--logger", help="use logging config file", nargs=1)
		args = vars(parser.parse_args())

		if args['server']:
			self._mqttServerHost = args['server'][0]
			self._config['host'] = self._mqttServerHost

		if args['port']:
			self._mqttServerPort = args['port'][0]
			self._config['port'] = self._mqttServerHost
			
		if args['logger'] and os.path.isfile(args['logger']):
			logging.config.fileConfig(args['logger'])
			if args['debug']:
				self._logger = logging.getLogger('debug')
				self._logger.setLevel(logging.DEBUG)
			else:
				self._logger = logging.getLogger('production')
				self._logger.setLevel(logging.INFO)
		elif os.path.isfile('logging.ini'):
			logging.config.fileConfig('logging.ini')
			if args['debug']:
				self._logger = logging.getLogger('debug')
				self._logger.setLevel(logging.DEBUG)
			else:
				self._logger = logging.getLogger('production')
				self._logger.setLevel(logging.INFO)
		else:
			if args['debug']:
				self._logger = logging.getLogger('debug')
				self._logger.setLevel(logging.DEBUG)
			else:
				self._logger = logging.getLogger('production')
				self._logger.setLevel(logging.INFO)
			ch = logging.FileHandler(APPLICATIONNAME + '.log', 'w')
			ch.setLevel(logging.INFO)
			self._logger.addHandler(ch)
		
		with open(CONFIG_FILE, 'w') as conffile:
			yaml.dump(self._config, conffile, default_flow_style = False)
			
		self.start()
			
	#__________________________________________________________________
	def build(self):
		# return a Button() as a root widget
		return Button(text='hello world!!!')

	#__________________________________________________________________
	def isConnectedToMqttBroker(self):
		return self._mqttConnected

	#__________________________________________________________________
	def _mqttOnConnect(self, client, userdata, flags, rc):
		if rc == 0:
			self._mqttConnected = True
			#self._logger.debug("Connected to MQTT server with flags: ", flags) # flags is dict
			self._logger.info("Program connected to MQTT server")
			if self._mqttOutbox:
				try:
					message = "CONNECTED"
					(result, mid) = self._mqttClient.publish(self._mqttOutbox, message, qos=MQTT_DEFAULT_QoS, retain=True)
					self._logger.info("{0} '{1}' (mid={2}) on {3}".format("Program sending message", message, mid, self._mqttOutbox))
				except Exception as e:
					self._logger.error("{0} '{1}' on {2}".format("MQTT API : failed to call publish() for", message, self._mqttOutbox))
					self._logger.debug(e)
			for topic in self._mqttSubscriptions:
				try:
					(result, mid) = self._mqttClient.subscribe(topic, MQTT_DEFAULT_QoS)
					self._logger.info("{0} (mid={1}) : {2}".format("Program subscribing to topic", mid, topic))
				except Exception as e:
					self._logger.error("MQTT API : failed to call subscribe()")
					self._logger.debug(e)
		elif rc == 1:
			self._logger.warning("Program failed to connect to MQTT server :  connection refused - incorrect protocol version")
		elif rc == 2:
			self._logger.warning("Program failed to connect to MQTT server : connection refused - invalid client identifier")
		elif rc == 3:
			self._logger.warning("Program failed to connect to MQTT server : connection refused - server unavailable")
		elif rc == 4:
			self._logger.warning("Program failed to connect to MQTT server : connection refused - bad username or password")
		elif rc == 5:
			self._logger.warning("Program failed to connect to MQTT server : connection refused - not authorised")
		else:
			self._logger.warning("{0} {1}".format("Program failed to connect to MQTT server : return code was"), rc)

		self.onConnect(client, userdata, flags, rc)

	#__________________________________________________________________
	def _mqttOnDisconnect(self, client, userdata, rc):
		self._mqttConnected = False
		self._logger.info("Program disconnected from MQTT server")

		serv = ''
		if isinstance(userdata, str):
			try:
				mydata = eval(userdata)
				if isinstance(mydata, dict) and 'host' in mydata and 'port' in mydata:
					serv = mydata['host'] + ':' + str(mydata['port'])
			except Exception as e:
				self._logger.debug("MQTT client userdata not as expected")
				self._logger.debug(e)

		if serv:
			self._logger.warning("{0}{1} {2} {3}".format("Disconnected from MQTT server with rc=", rc, "from", serv))
		else:
			self._logger.warning("{0}{1}".format("Disconnected from MQTT server with rc=", rc))

		self.onDisconnect(client, userdata, rc)

	#__________________________________________________________________
	def _mqttOnLog(self, client, userdata, level, buf):
		self._logger.debug("Paho log level {0} : {1}".format(level, buf))

	#__________________________________________________________________
	def _mqttOnMessage(self, client, userdata, msg):
		message = None
		try:
			message = msg.payload.decode(encoding="utf-8", errors="strict")
		except:
			pass

		if message:
			self._logger.info("Message received : '" + message + "' in " + msg.topic)
			if msg.topic == self._mqttInbox and message == "@PING":
				self._publishMessage(self._mqttOutbox, "PONG")
			else:
				self.onMessage(msg.topic, message)
		else:
			self._logger.warning("{0} {1}".format("MQTT message decoding failed on", msg.topic))

	#__________________________________________________________________
	def _mqttOnPublish(self, client, userdata, mid):
		self._logger.debug("MQTT message is published : mid=%s userdata=%s", mid, userdata)
		self._logger.info("{0} (mid={1})".format("Message published", mid))

	#__________________________________________________________________
	def _mqttOnSubscribe(self, client, userdata, mid, granted_qos):
		self._logger.debug("MQTT topic is subscribed : mid=%s granted_qos=%s", mid, granted_qos) # granted_qos is (2,)
		self._logger.info("{0} (mid={1}) {2} {3}".format("Program susbcribed to topic", mid, "with QoS", granted_qos))  # mid is a number (count)

	#__________________________________________________________________
	def _mqttOnUnsubscribe(self, client, userdata, mid):
		self._logger.debug("MQTT topic is unsubscribed : mid=%s", mid)
		self._logger.info("{0} (mid={1})".format("Program has been unsusbcribed from topic", mid))

	# __________________________________________________________________
	def onConnect(self, client, userdata, flags, rc):
		# extend as a virtual method
		pass

	# __________________________________________________________________
	def onDisconnect(self, client, userdata, rc):
		# extend as a virtual method
		pass

	#__________________________________________________________________
	def onMessage(self, topic, message):
		# extend as a virtual method
		print(topic, message)
		self._publishMessage(self._mqttOutbox, "OMIT " + message)

	#__________________________________________________________________
	def _publishMessage(self, topic, message):

		if not topic:
			self._logger.warning("{0} : '{1}'".format("Program failed to send message (no topic)", message))
		elif self._mqttConnected:
			try:
				(result, mid) = self._mqttClient.publish(topic, message, qos=MQTT_DEFAULT_QoS, retain=False)
				self._logger.info("{0} '{1}' (mid={2}) on {3}".format("Program sending message", message, mid, topic))
			except Exception as e:
				self._logger.error("{0} '{1}' on {2}".format("MQTT API : failed to call publish() for", message, topic))
				self._logger.debug(e)
		else:
			self._logger.warning("{0} : '{1}'".format("Program failed to send message (disconnected)", message))

	#__________________________________________________________________
	def start(self):	
				
		if self._mqttOutbox:
			try:
				self._mqttClient.will_set(self._mqttOutbox, payload="DISCONNECTED", qos=1, retain=True)
			except Exception as e:
				self._logger.error("MQTT API : failed to call will_set()")
				self._logger.debug(e)
			
		mydata = { 'host': self._mqttServerHost, 'port': self._mqttServerPort }
		self._mqttClient.user_data_set(str(mydata))

		'''
		The loop_start() starts a new thread, that calls the loop method at 
		regular intervals for you. It also handles re-connects automatically.
		'''
		self._mqttClient.loop_start()
		
		'''
		If you use client.connect_async(), your client must use the 
		threaded interface client.loop_start()
		'''
		try:
			self._mqttClient.connect_async(self._mqttServerHost, port = self._mqttServerPort, keepalive = MQTT_KEEPALIVE)
		except Exception as e:
			self._logger.error("MQTT API : failed to call connect_async()")
			self._logger.debug(e)


	# __________________________________________________________________
	def addData(self, data):
		self._publishable.append(data)

	# __________________________________________________________________
	def addPeriodicAction(self, title, func, time):
		if title in self._periodicActions:
			self._logger.warning("Duplicate periodic action ignored '{0}' every {1} seconds".format(title, time))
		else:
			self._periodicActions[title] = (func, time)
			self._logger.info("New periodic action added '{0}' every {1} seconds".format(title, time))

	# __________________________________________________________________
	def removeData(self, data):
		self._publishable.remove(data)

	# __________________________________________________________________
	def sendData(self, data):
		self._publishMessage(self._mqttOutbox, "DATA " + data)


	# __________________________________________________________________
	def sendDone(self, action):
		self._publishMessage(self._mqttOutbox, "DONE " + action)


	# __________________________________________________________________
	def sendMesg(self, message, topic=None):
		if topic is None:
			self._publishMessage(self._mqttOutbox, "MESG " + message)
		else:
			self._publishMessage(topic, "MESG " + message)


	# __________________________________________________________________
	def sendOmit(self, action):
		self._publishMessage(self._mqttOutbox, "OMIT " + action)


	# __________________________________________________________________
	def sendOver(self, challenge):
		self._publishMessage(self._mqttOutbox, "OVER " + challenge)


	# __________________________________________________________________
	def sendProg(self, program):
		self._publishMessage(self._mqttOutbox, "PROG " + program)


	# __________________________________________________________________
	def sendRequ(self, request, topic=None):
		if topic is None:
			self._publishMessage(self._mqttOutbox, "REQU " + request)
		else:
			self._publishMessage(topic, "REQU " + message)