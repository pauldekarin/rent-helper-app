from Utility.observer import Observer

class FavouriteScreenModel:
	def __init__(self):
		self._observers = []
		self._data = {}

	
	def onStart(self):
		pass
	def setComment(self, url, comment):
		self.notify_observer(
			Observer.ObserverEvent(Observer.ObserverEvent.SET_COMMENT),
			{'url':url, 'comment':comment}
		)

	def setFavourite(self, favourite, data:dict):
		
		if favourite:
			self._data.update(data)
			self.notify_observer(
				Observer.ObserverEvent(Observer.ObserverEvent.SET_FAVOURITE), 
				data)
		else:
			self.notify_observer(
				Observer.ObserverEvent(Observer.ObserverEvent.REMOVE_FAVOURITE),
				{'url':data['url']}
			)


	def set(self, data):
		self._data = data
		self.notify_observer()
		
	def refresh(self):

		self.notify_observer()
	
	def set_favourite(self, card, favourite):
		pass

	def add_observer(self, observer):
		self._observers.append(observer)

	def remove_observer(self, observer):
		self._observers.remove(observer)
		
	def refresh_comments(self, comments):
		for url, card in self._data.items():
			if url in comments:
				card['comment'] = comments[url]

		self.notify_observer(t = Observer.COMMENT_CHANGE)

	def notify_observer(self, event:Observer.ObserverEvent, data:dict):
		for observer in self._observers:
			observer.model_is_changed(event, data)