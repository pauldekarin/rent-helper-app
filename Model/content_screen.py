from Utility.parser import Parser
from Utility.observer import Observer

from typing import Union
from threading import Timer
import asyncio
import sys
import json
from Utility.db import DataBase

class ContentScreenModel:

	_data = {}

	@property
	def data(self):
		return self._data
	@data.setter
	def data(self, data):
		self._data = data
		self.notify_observer()

	def __init__(self):
		self._observers = []
		self._data = {}


	def update(self, js:dict):
		self._data[js['platform']] = js['data']

		self.notify_observer(
			Observer.ObserverEvent(Observer.ObserverEvent.DATA),
			self._data
		)

	def onStart(self):
		pass


	def setFavourite(self, url, platform, favourite):
		self.notify_observer(
			Observer.ObserverEvent(Observer.ObserverEvent.SET_FAVOURITE) if favourite 
				else Observer.ObserverEvent(Observer.ObserverEvent.REMOVE_FAVOURITE), 
			{'url':url,'platform':platform})
		
	def setComment(self, platform, url, comment):
		self.notify_observer(
			Observer.ObserverEvent(Observer.ObserverEvent.SET_COMMENT),
			{'url':url, 'comment':comment, 'platform':platform}
		)

	def parserHandler(self, resp):
		if resp['status'] == 'DATA':
			self._data = resp['data']
			self.notify_observer(Observer.ObserverEvent(Observer.ObserverEvent.DATA), self._data)
		
		

	def add_observer(self, observer):
		self._observers.append(observer)

	def remove_observer(self, observer):
		self._observers.remove(observer)
		
	def notify_observer(self, event, data):
		for observer in self._observers:
			observer.model_is_changed(event, data)