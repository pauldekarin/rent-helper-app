class ObserverEvent:
	DATA = 1
	SET_COMMENT = 2
	SET_FAVOURITE = 3
	REMOVE_FAVOURITE = 4
	EXTRA = 5
	AUTHENTICATION = 6
	LOGOUT = 7
	ADD = 8

	def __init__(self, type) -> None:
		self._type = type

	def type(self):
		return self._type

class Observer:
	ObserverEvent = ObserverEvent

	def model_is_changed(self, data:dict):
		pass