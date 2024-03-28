from View.FavouriteScreen.favourite_screen import FavouriteScreenView
from Utility.db import DataBase

class FavouriteScreenController:
	def __init__(self, model, m_controller = None, name = None):
		self.model = model
		self.view = FavouriteScreenView(model = self.model, controller = self)

		self.m_controller = m_controller
		self.name = name
	
	def onStart(self):
		self.m_controller.onStart(self.name)
		
	def onFavourite(self, favourite, data):
		self.m_controller.onFavourite(
			c_name = self.name, 
			favourite = favourite,
			data =  data
			)
	def onComment(self, comment, data):
		self.m_controller.onComment(
			c_name = self.name,
			comment = comment,
			data = data
		)
		
	def setFavourite(self, favourite, data):
		self.model.setFavourite(favourite, data)
		
	def setComment(self, url, comment):
		self.model.setComment(url, comment)
		
	def on_start(self):
		self.m_controller.on_start(name_screen = self.view.name)
	
	def set(self, data):
		self.model.set(data)
		
	def on_favourite(self, card, favourite):
		self.m_controller.favourite(name_screen = self.view.name, card = card, favourite = favourite)

	def on_comment(self, card, comment):
		self.m_controller.comment(name_screen = self.view.name, card = card, comment = comment)
	
	def refresh_comments(self, comments):
		self.model.refresh_comments(comments)

	def get_view(self):
		return self.view