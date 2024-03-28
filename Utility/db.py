import sqlite3 as sql
import time
from Utility.path import Path


class DataBase:
	def __init__(self, db_name = Path.database()):
		self.db_name = db_name
		self.con = sql.connect(db_name, check_same_thread=False)
		self.con.row_factory = sql.Row

		self.cur = self.con.cursor()

		self.names = {
			'history':['city','price','rooms','time']
		}

		self.build_cards()
		self.build_history()
		self.build_credentials()
		
	def __del__(self):
		self.close()
	
	def close(self):
		self.con.commit()
		self.con.close()

	def build_history(self):
		self.cur.execute('''CREATE TABLE IF NOT EXISTS 'history' (
				'city' STRING,
				'price' STRING,
				'rooms' STRING,
				'timestamp' REAL
			)''')

	def build_cards(self):
		self.cur.execute('''CREATE TABLE IF NOT EXISTS 'cards' 
				(
					'url' STRING, 
					'img_sources' STRING, 
					'title' STRING, 
					'subway_name' STRING,
					'subway_time' STRING,
					'address' STRING,
					'price' STRING,
					'meta' STRING,
					'description' STRING,
					'favourite' TINYINT(1),
					'comment' STRING,
				   	'time' STRING,
					'platform' STRING
				)''')
	
	def build_credentials(self):
		self.cur.execute('''CREATE TABLE IF NOT EXISTS 'credentials'
				   (
						'username' STRING,
						'password' STRING
				   )''')
	
	def convertList(self, l, invert = False):
		return '|'.join(l) if not invert else l.strip('|')
	
	def credentials(self, username, password):
		self.clear_credentials()
		
		self.cur.execute(f'INSERT INTO credentials (username, password) VALUES("{username}", "{password}")')

		self.con.commit()
		
	
	
	def card(self, card:dict):
		self.cur.execute(f'SELECT title FROM cards WHERE url = "{card["url"]}"')

		if type(card['img_sources']) == list:
			card['img_sources'] = self.convertList(map(str,card['img_sources']))

		#FAVOURITE
		if 'favourite' in card:
			card['favourite'] = 1 if card['favourite'] else 0 
		else:
			card['favourite'] = 0
		
		#COMMENT
		if 'comment' not in card:
			card['comment'] = ''

		else:
			for key in card.keys():
				if isinstance(card[key], str):
					card[key] = card[key].replace('"', "'")
					
			if self.cur.fetchone() == None:
				
				self.cur.execute('''INSERT INTO cards ({names}) VALUES({values})'''.format(
						names = ','.join(f'{k}' for k in card.keys()),
						values = ','.join(f'"{v}"' for v in card.values())
					))
			else:
				
				self.cur.execute('''UPDATE cards SET {values} WHERE url = "{url}" '''.format(
								values = ','.join(f'{k}="{v}"' for k, v in card.items() if k != 'url'),
								url = card['url']
					))

		self.con.commit()
	def removeCard(self, url):
		self.cur.execute(f'DELETE from cards WHERE url = "{url}"')
		self.con.commit()

	def add_history(self, city:str, price:list, rooms:list, timestamp:float):
		price = '|'.join(price)
		rooms = '|'.join(rooms)

		self.cur.execute(
			'''
				INSERT INTO history ("city", "price","rooms","timestamp") VALUES("%s", "%s", "%s", "%f")
			''' % (city, price, rooms, timestamp)
		)
		self.con.commit()

	def get_histories(self):
		self.cur.execute('SELECT * FROM history')
		
		return [{
				'city':row['city'],
				'price':row['price'].split('|'),
				'rooms':row['rooms'].split('|'),
				'timestamp':row['timestamp'],
			}
				for row in self.cur.fetchall()
			]

	def history(self, data):
		if type(data['price']) == list:
			if data['price'][0] == '0' or not data['price'][0].isdigit():
				data['price'][0] = 0

			if data['price'][1] == '0' or not data['price'][1].isdigit():
				data['price'][1] = 0

			data['price'] = '|'.join(map(str, data['price']))

		if type(data['rooms']) == list:
			data['rooms'] = '|'.join(data['rooms'])

		if 'timestamp' not in data:
			data['timestamp'] = time.time()

		
		
		self.cur.execute('''INSERT INTO history ({names}) VALUES(
			{val}
			)'''.format(
					val = ",".join([f"\"{v}\"" for v in data.values()]),
					names = ",".join(f"{k}" for k in data.keys())
						))


		self.con.commit()

		return self.cur.fetchone()
	def get_cards(self):
		self.cur.execute('SELECT * FROM cards')
		d = {}
		for row in self.cur.fetchall():
			s = dict(row)
			s['img_sources'] = self.convertList(s['img_sources'], invert=True)
			d[s['url']] = s 
		return d

	
	def get_credentials(self):
		self.cur.execute('SELECT * FROM credentials')
		res = self.cur.fetchone()

		if res != None:
			return dict(res)
		else:
			return None
	
	def fetchall_converted(self):

		return [dict(row) for row in self.cur.fetchall()]


	def get_favourites(self):
		self.cur.execute('SELECT * FROM cards WHERE favourite=1')
		d = []
		for row in self.cur.fetchall():
			s = dict(row)
			s['img_sources'] = s['img_sources'].split('|')
			d.append(s)
		return d

	def get_comments(self):
		self.cur.execute('SELECT url, comment FROM cards WHERE length(comment) > 0')
		return {str(item[0]):str(item[1]) for item in self.cur.fetchall()}
	
	def clear_credentials(self):
		self.cur.execute('DELETE FROM credentials')
		self.con.commit()


	
