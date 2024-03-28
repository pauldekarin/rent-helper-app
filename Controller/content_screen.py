from View.ContentScreen.content_screen import ContentScreenView

class ContentScreenController:
	def __init__(self, model, m_controller = None, name = None):
		self.model = model
		self.view = ContentScreenView(model = model, controller = self)
		self.m_controller = m_controller
		self.name = name
	
	def update(self, js:dict):
		self.model.update(js)

	def onPage(self, plName, page):
		self.m_controller.onPage(plName, page)
		
	def onFavourite(self, favourite, data):
		
		self.m_controller.onFavourite(
			c_name = self.name,
			favourite = favourite,
			data = data
		)
	def onComment(self, comment, data):
		self.m_controller.onComment(
			c_name = self.name,
			comment = comment,
			data = data,
		)
	def setFavourite(self, url, platform, favourite):
		self.model.setFavourite(url, platform, favourite)

	def setComment(self, 
				platform:str, 
				url:str,
				comment:str):
		
		self.model.setComment(platform, url, comment)
	
	def onStart(self):
		pass
	def onApply(self, city,price, rooms):
		self.m_controller.onFilter(
			name_screen = self.name,
			city = city,
			price = price,
			rooms = rooms
		)
	def setFilter(self, city:str, price:list, rooms:list):
		self.view.setFilter(city = city, price = price, rooms = rooms)
		
	def on_start(self):
		self.m_controller.on_start(name_screen = self.view.name)

	def on_comment(self, card:dict, comment:str):
		self.m_controller.comment(name_screen = self.view.name, card = card, comment = comment)

	def on_favourite(self, card, favourite):
		self.m_controller.favourite(name_screen = self.view.name, card = card, favourite = favourite)
		
	def set(self, **kwargs):
		self.model.set(**kwargs)

	def refresh(self, t = None):
		self.model.refresh()

	def get_view(self)->ContentScreenView:
		return self.view

	def change_filter(self, name, value):
		self.model.change_filter(name, value)

	def set_filter(self, f):
		self.view.set_filter(f)
	
	def set_basecards(self, data):
		self.model.set_basecards(data)
		
	def apply_filter(self):
		if self.model._filter['city']:
			self.m_controller.history(name_screen = self.view.name, data = self.model._filter)
			self.model.apply_filter()