from Utility.db import DataBase

class MainScreenModel:
	def __init__(self):
		self._observers = []
		self._db = DataBase()
		
	def favourite(self, card, favourite):
		self._db.card(card = card, favourite = favourite)

	def comment(self, card:dict, comment:str):
		self._db.card(card = card, comment = comment)

	def load_favourites(self):
		self._db.get_favourites()
	
	def add_observer(self, observer):
		self._observers.append(observer)

	def remove_observer(self, observer):
		self._observers.remove(observer)
		
	def notify_observer(self):
		for observer in self._observers:
			observer.model_is_changed()