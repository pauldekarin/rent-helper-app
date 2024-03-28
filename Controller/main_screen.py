from Utility.db import DataBase
from Utility.parser import Parser, UrlFormer
from Utility.firebase import Firebase
from Utility.path import Path

from View.screens import screens

import json
import logging
import time

class MainController():
	def __init__(self):
		self.view = None

		self.controllers = {}

		self.db = DataBase()

		self.parser = Parser()
		self.parser.set_callback(self.parserCallback)

		self.firebase = Firebase()

		self.former = UrlFormer(headless=False)
		self.former.setAsync(True)
		self.former.connect(self.applyUrls)
		
		

		with open(Path.json('platforms.json')) as f_in:
			for name, data in json.load(f_in).items():
				self.parser.inflate(name, data['xpath'])
		
		self.updateDatabaseCards()

	def get_view(self):
		return self._view

	def __test__(self):
		self.parser.apply_url('cian','https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=1&sort=creation_date_desc&type=4')
		self.parser.apply_url('avito','https://www.avito.ru/novosibirsk/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg?cd=1&s=104')
		self.parser.run()

	def updateDatabaseCards(self):
		self.dbCards = self.db.get_cards()
	
	def parserCallback(self, msg:dict):
		if msg['status'] == 'DATA':
			for url in msg['data']['cards'].keys():
				if url in self.dbCards:
					msg['data']['cards'][url]['favourite'] = self.dbCards[url]['favourite']
					msg['data']['cards'][url]['comment'] = self.dbCards[url]['comment']

			self.controllers['content screen'].update({'data':msg['data'],'platform':msg['platform']})

			
		
		elif msg['status'] == 'NO_CARDS':
			self.controllers['content screen'].update({'data':None, 'platform':msg['platform']})
		

	def addController(self, name, instance):
		self.controllers[name] = instance
	def adjustLocalToCloudDataBase(self):
		for _fb_card in self.firebase.get_data():
			pass

	

	def onStart(self):
		# self.__test__()
		
		logging.info('Get User Credentials')

		#History
		for row in self.db.get_histories():
			self.controllers['history screen'].add(**row)

		
		#Authentication
		res = self.db.get_credentials()

		if res:
			logging.info('Sign In %s' % res['username'])
			if self.firebase.sign_in(res['username'], res['password']):
				logging.info('Sign In Success')
				
				#Auth on User Screen
				self.controllers['user screen'].setUser(self.firebase.get_user_info())

				logging.info('Get Favourites From Cloud Data')
				#Inflate Favourite Screen from Cloud
				cloudData = self.firebase.get_data()

				for url, data in cloudData.items():
					if data['favourite']:
						self.controllers['favourite screen'].setFavourite(True, data)
				
				#Set streaming on cloud data chahnged
				self.firebase.set_stream(self.streamHandler)

				self.adjustLocalToCloudDataBase()
				return
		
		#Inflate Favourite Screen from Local Hadrware
		localFavourites = self.db.get_favourites()

		for data in localFavourites:
			self.controllers['favourite screen'].setFavourite(True, data)
		
		
	def streamHandler(self, msg):
		pass

	def onLogout(self):
		logging.info('Logout %s' % self.firebase.user.auth.current_user.email)
		self.firebase.logout()
		
	def onSignIn(self, username,password):
		if not self.firebase.authorized():
			logging.info('Sig In %s' % username)
			
			res = self.firebase.sign_in(username, password)

			if res:
				logging.info('Sign In Success!')
				self.controllers['user screen'].setUser(self.firebase.get_user_info())
				self.db.credentials(username, password)

			else:
				logging.error('Sign In Failed')

		
	def onSignUp(self, username, password):
		if not self.firebase.authorized():
			res = self.firebase.sign_up(username, password)

			if res:
				self.controllers['user screen'].setUser(self.firebase.get_user_info())
				self.db.credentials(username, password)

	def onFilter(self, name_screen:str, city:str, price:list, rooms:list)->None:
		self.former.setCity(city)
		self.former.setFilter(price = price, rooms = rooms)
		self.former.form()

		if name_screen == 'content screen':
			logging.info('Apply Filter {}, {}/{}, {}'.format(
				city, price[0] if price[0] else 0,price[1] if price[1] else 'Infinity',' '.join(rooms)
			))
			self.controllers['history screen'].add(city = city, price = price, rooms = rooms)
			self.db.add_history(
				city = city,
				price = price,
				rooms = rooms,
				timestamp = time.time()
			)

		elif name_screen == 'history screen':
			self.controllers['content screen'].setFilter(city = city, price = price, rooms = rooms)
			self.view.setScreen(screens['content screen']['name'])

	def applyUrls(self, urls):
		for plName, url in urls.items():
			self.parser.apply_url(plName, url)

		self.parser.refresh()

	def onClose(self):
		logging.info('Closing APP')

		self.parser.stop()
		self.firebase.stop_stream()
		self.db.close()
		self.former.stop()
		
	def onPage(self, plName:str, page)->None:
		logging.info('Page %s %s',plName.upper(), page)

		self.parser.page(plName, page)


	def onFavourite(self, c_name:str, favourite:bool, data:dict):
		logging.info('{} Favourite {}'.format('Set' if favourite else 'Remove', data['url']))

		if c_name == 'content screen':
			self.controllers['favourite screen'].setFavourite(favourite, data)

		elif c_name == 'favourite screen':
			self.controllers['content screen'].setFavourite(
				url = data['url'], 
				platform = data['platform'], 
				favourite = favourite)

		
		if favourite:
			self.firebase.push(
				id = data['url'], 
				data = data)
			self.db.card(data)
			
		elif data['comment'] == '':
			self.firebase.remove(data['url'])
			self.db.removeCard(data['url'])


	def onComment(self, c_name:str, comment:str, data:dict):
		logging.info('Set Comment {}: "{}" '.format(data['url'], comment))

		if comment:
			self.firebase.push(
				id = data['url'], 
				data = data)
			self.db.card(data)

		elif data['favourite'] == False:
			self.firebase.remove(data['url'])
			self.db.removeCard(data['url'])

		if c_name == 'favourite screen':
			self.controllers['content screen'].setComment(
				platform = data['platform'],
				comment = comment,
				url = data['url']
			)
		
		elif c_name == 'content screen':
			self.controllers['favourite screen'].setComment(
				comment = comment,
				url = data['url']
			)

			
