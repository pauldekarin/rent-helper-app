from View.HistoryScreen.history_screen import HistoryScreenView
from typing import Optional

class HistoryScreenController:
	def __init__(self, model, m_controller = None, name = None):
		self.model = model
		self.view = HistoryScreenView(model = model, controller = self)
		self.m_controller = m_controller
		self.name = name

	def add(self, city:str, price:list, rooms:list, timestamp:Optional[float] = None)->None:
		self.model.add(
			city = city, 
			price = price, 
			rooms = rooms, 
			timestamp = timestamp)
	
	def onApply(self, row):
		self.m_controller.onFilter(
			name_screen = self.name,
			city = row['city'],
			price = row['price'],
			rooms = row['rooms']
		)

	def on_create(self):
		self.model.on_create()
	def set_filter(self, f):
		self.m_controller.set_filter(self.view.name, f)
		
	def get_view(self):
		return self.view