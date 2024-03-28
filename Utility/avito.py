from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import time
import datetime

from accessify import protected


class Avito():
	url = 'https://www.avito.ru/{city}/nedvizhimost'
	xpath = {
		'link':'//a[@data-marker="search-form-widget/action-button-0"]',

		'roomsButton':'//div[@data-marker="params[550]"]',
		'roomsListBox':'//div[@data-marker="params[550]/tooltip"]',

		'rooms':{
			'studio':'//label[@data-marker="params[550](5702)/5702"]',
			'1':'//label[@data-marker="params[550](5703)/5703"]',
			'2':'//label[@data-marker="params[550](5704)/5704"]',
			'3':'//label[@data-marker="params[550](5705)/5705"]',
			'4':'//label[@data-marker="params[550](5706)/5706"]',
			'5+':'//label[@data-marker="params[550](5707)/5707"]',
			'free':'//label[@data-marker="params[550](5708)/5708"]',
		},

		'priceButton':'//div[@data-marker="price"]',
		'priceListBox':'//div[@data-marker="price/tooltip"]',

		'price':{
			'priceFrom':'//input[@data-marker="price/inputs/from"]',
			'priceTo':'//input[@data-marker="price/inputs/to"]'
		}
	}
	def __init__(self, city = 'moskva', filter = {}, timeout = 10, headless = True):
		self.options = Options()
		self.options.add_experimental_option('detach',True)
		self.options.set_capability('pageLoadStrategy','eager')
		if (headless): self.options.add_argument('--headless=new')

		self.driver = webdriver.Chrome(options = self.options)

		self.city = city
		self.wait = WebDriverWait(self.driver, timeout)
		self.filter = filter

		self.__open__()


	def __open__(self):
		self.driver.get(self.url.format(city = self.city))


		try:
			self.link = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath['link']))).get_attribute('href')
		except TimeoutException as e:
			try:
				self.driver.find_element(By.CLASS_NAME, 'firewall-container')
				self.driver.refresh()
				self.link = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath['link']))).get_attribute('href')
			except NoSuchElementException as noe:
				print(noe)


		self.wait.until(EC.presence_of_element_located(
			(By.XPATH, '//input[@data-marker="params[201]"]')
			)).find_element(By.XPATH, '..').click()
		self.wait.until(EC.presence_of_element_located((
				By.XPATH,'//div[@role="listbox"]/div/div[2]'
			))).click()

		self.__wait__()
		self.__filter__()

	@protected
	def __filter__(self):
		if 'rooms' in self.filter.keys():
			self.wait.until(EC.presence_of_element_located(
					(By.XPATH, self.xpath['roomsButton'])
				)).click()
			self.wait.until(EC.presence_of_element_located(
					(By.XPATH, self.xpath['roomsListBox'])
				))

			for r in self.filter['rooms']:
				while True:
					self.wait.until(EC.presence_of_element_located(
							(By.XPATH, self.xpath['rooms'][r])
						)).click()
					if (self.driver.find_element(By.XPATH, self.xpath['rooms'][r]).get_attribute('aria-checked') == 'true'):
						break
				

			self.__wait__()

		if 'price' in self.filter.keys():
			self.wait.until(EC.presence_of_element_located(
					(By.XPATH, self.xpath['priceButton'])
				)).click()
			self.wait.until(EC.presence_of_element_located(
					(By.XPATH,self.xpath['priceListBox'])
				))

			self.wait.until(EC.presence_of_element_located(
					(By.XPATH, self.xpath['price']['priceFrom'])
				)).send_keys(self.filter['price'][0])

			self.__wait__()

			self.wait.until(EC.presence_of_element_located(
					(By.XPATH, self.xpath['price']['priceTo'])
				)).send_keys(self.filter['price'][1])
			self.__wait__()

			
	@protected
	def __wait__(self):
		while True:
			try:
				if (self.driver.find_element(By.XPATH, self.xpath['link']).get_attribute('href') != self.link):
					break
			except StaleElementReferenceException as e:
				None
		self.link = self.driver.find_element(By.XPATH, self.xpath['link']).get_attribute('href')
		

	def __str__(self):
		return ''.join((self.link,'&s=104'))

	def __get__(self):
		self.driver.get(str(self))

	def get_url(self):
		return str(self)


