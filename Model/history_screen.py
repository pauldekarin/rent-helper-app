from Utility.observer import Observer
from Utility.date import Date

from typing import Optional

class HistoryScreenModel:
	def __init__(self):
		self._observers = []
		self._data = dict()

	def onStart(self):
		pass
	def on_create(self):
		self.notify_observer()

	def add(self, city:str, price:list, rooms:list, timestamp:Optional[float] = None)->None:
		self._data[Date.date()] = {
			'city':city,
			'price':price,
			'rooms':rooms,
			'time':Date.time(timestamp = timestamp)
		}
		
		self.notify_observer(Observer.ObserverEvent(Observer.ObserverEvent.ADD), {
			'date':Date.date(timestamp = timestamp),
			'data':{
				'city':city,
				'price':price,
				'rooms':rooms,
				'time':Date.time(timestamp = timestamp)
			}
		})

	def add_observer(self, observer)->None:
		self._observers.append(observer)

	def remove_observer(self, observer)->None:
		self._observers.remove(observer)
		
	def notify_observer(self,t:Observer.ObserverEvent, data:dict)->None:
		for observer in self._observers:
			observer.model_is_changed(t, data)