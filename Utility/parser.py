from collections.abc import Callable, Iterable, Mapping
from threading import Thread, Event
from threading import enumerate as get_threads
import multiprocessing
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_
import ssl
import requests
import os, signal
import json
from lxml import html, etree
import re
from typing import Any, Callable
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from typing import Optional
import time
import datetime
import asyncio

from accessify import protected
from Utility.path import Path

# if __name__ == '__main__':
#     from path import Path
# else:
#     from Utility.path import Path


class TlsAdapter(HTTPAdapter):
    CIPHERS = """ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"""

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(ciphers=self.CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)


# class ModifiedThread(Thread):
#     def __init__(self, group: None = None, target: Callable[..., object] or None = None, name: str or None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] or None = None, *, daemon: bool or None = None) -> None:
#         super().__init__(group, target, name, args, kwargs, daemon=daemon)
#         self._event = Event()
    
#     def stop(self):
#         self._event.set()

class UrlFormer():

    def get_avito_url(self)->str:
        link = ''

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

        def _wait():
            nonlocal link
            nonlocal xpath

            while True:
                """
                For Every "Action" We Had To Wait
                For Link Changing To Check if "Action" Has Been Applied On Page
                """
                try:
                    if (driver.find_element(
                            By.XPATH, xpath['link']).get_attribute('href') != link):
                        break
                except StaleElementReferenceException as e:
                    pass
            

            link = driver.find_element(By.XPATH, xpath['link']).get_attribute('href')
        
        

        #Set Options Attributes For Selenimu Chrome WebDriver
        options = Options()
        options.add_experimental_option('detach',True)
        options.set_capability('pageLoadStrategy','eager')
        options.add_argument("--disable-notifications")
        if (self.headless): 
            options.add_argument('--headless=new')

        #Initialize Driver
        driver = webdriver.Chrome(options = options)
        self._drivers.append(driver)
        
        #Initialize Default Wait Util
        wait = WebDriverWait(driver, self.timeout)

        try:
            #Load Page for Specified City
            driver.get(self.cities[self.city]['avito']['url'])

            #Check if WebDriver has not been banned
            while True:
                try:
                    link = wait.until(EC.presence_of_element_located((By.XPATH, xpath['link']))).get_attribute('href')

                    break
                except TimeoutException:
                    #Check If On Loading Page We Get Captcha Verification
                    if driver.find_elements(By.CLASS_NAME, 'firewall-container'):
                        driver.refresh()
                    else:
                        driver.quit()
                        self._drivers.remove(driver)
                        raise Exception('Cant Open Page %s' % self.cities[self.city]['avito']['url'])
            
            #Change Search Filters from "Buy" to "Rent"
            wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@data-marker="params[201]"]')
                    )).find_element(By.XPATH, '..').click()
            wait.until(EC.presence_of_element_located((
                    By.XPATH,'//div[@role="listbox"]/div/div[2]'
                ))).click()

            _wait()

            #If We Have Rooms In Filter
            if len(self.filter['rooms']) > 0:
                #Open Rooms Filter Popup
                wait.until(EC.presence_of_element_located(
                        (By.XPATH, xpath['roomsButton'])
                    )).click()
                wait.until(EC.presence_of_element_located(
                            (By.XPATH, xpath['roomsListBox'])
                        ))
                
                #Apply Necessary CheckBoxes
                for r in self.filter['rooms']:
                    t = 0
                    while True:
                        checkBox = wait.until(EC.presence_of_element_located(
                                        (By.XPATH, xpath['rooms'][r])
                                    ))
                        checkBox.click()
                        
                        if (checkBox.get_attribute('aria-checked') == 'true'):
                            break

                        elif t > 10:
                            driver.quit()
                            raise TimeoutError()
                        
                        t += 1
                
                _wait()
            
            #If We Have Price in Filter
            if self.filter['price'][0] != '' and self.filter['price'][1] != '':
                #Open On Page Price Popup
                wait.until(EC.presence_of_element_located(
                        (By.XPATH, xpath['priceButton'])
                    )).click()
                wait.until(EC.presence_of_element_located(
                        (By.XPATH, xpath['priceListBox'])
                    ))

                if self.filter['price'][0] != '' and int(self.filter['price'][0]) > 0:
                    t = 0
                    while True:
                        try:
                            inp = wait.until(EC.presence_of_element_located(
                                (By.XPATH, xpath['price']['priceFrom'])
                            ))
                            inp.click()
                            
                            inp.send_keys(self.filter['price'][0])
                            
                            break
                        except Exception as te:
                            if t > 10:
                                driver.quit()
                                self._drivers.remove(driver)
                                raise TimeoutError()
                            
                            t += 1
                if self.filter['price'][1] != '':
                    t = 0
                    while True:
                        try:
                            inp = wait.until(EC.presence_of_element_located(
                                (By.XPATH, xpath['price']['priceTo'])
                            ))
                            inp.click()
                            
                            inp.send_keys(self.filter['price'][1])
                            
                            break
                        except Exception as te:
                            if t > 10:
                                driver.quit()
                                self._drivers.remove(driver)
                                raise TimeoutError()
                            
                            t += 1
                _wait()
            
            driver.quit()
            self._drivers.remove(driver)

            return f'{link}&s=104'
        
        except Exception as e:
            driver.quit()
            self._drivers.remove(driver)

            return link


    def get_cian_url(self):
        return '''
                https://cian.ru/cat.php?currency=2&deal_type=rent&engine_version=2&
                    maxprice={maxprice}&
                    minprice={minprice}&
                    offer_type=flat&
                    region={region}&
                    room1={room1}&
                    room2={room2}&
                    room3={room3}&
                    room4={room4}&
                    room5={room5}&
                    room6={room6}&
                    room7={free}&
                    room9={studio}&
                    type=4&
                    sort=creation_date_desc
                '''.format(
                        minprice = self.filter['price'][0] if self.filter['price'] != '' else '0',
                        maxprice = self.filter['price'][1] if self.filter['price'][1] != ''  else '9999999999',
                        room1 = 1 if '1' in self.filter['rooms'] else 0,
                        room2 = 1 if '2' in self.filter['rooms'] else 0,
                        room3 = 1 if '3' in self.filter['rooms'] else 0,
                        room4 = 1 if '4' in self.filter['rooms'] else 0,
                        room5 = 1 if '5+' in self.filter['rooms'] else 0,
                        room6 = 1 if '5+' in self.filter['rooms'] else 0,
                        free = 1 if 'free' in self.filter['rooms'] else 0,
                        studio = 1 if 'studio' in self.filter['rooms'] else 0,
                        region = self.cities[self.city]['cian']['region']
                    ).strip().replace('\n','').replace(' ','')


    
    
    _thread = None
    _callback = None
    _filter = dict()
    _city = str()
    _drivers = list()

    @property
    def drivers(self):
        return self._drivers
    
    @property
    def city(self):
        return self._city
    
    @property
    def filter(self):
        return self._filter
    
    @property
    def thread(self):
        return self._thread
    @property
    def callback(self):
        return self._callback
    
    def __init__(self, 
            timeout:Optional[int] = 10, 
            headless:Optional[bool] = False,
            isAsync:bool = False) -> None:
        """
        Form URL for Avito, Cian by Specified Attributes

        :attr "str" city - City 
        :attr "dict" filter - Include parameters as price and count of rooms
        :attr "int" timeout - As Avito requires to use driver, indicate timeout 
        :attr "headless" - As Avito requires to use driver, show proccess or hide it
        """
        self.headless = headless
        self.timeout = timeout
        self.isAsync = isAsync

        self.cities = json.load(open(Path.json('cities.json')))


    
    def connect(self, callback:Callable)->None:
        self._callback = callback
   
    def setTimeout(self, _tm:int)->None:
        self.timeout = _tm

    def setHeadless(self, _hl:bool)->None:
        self.headless = _hl

    def setFilter(self, price:Optional[list] = None, rooms:Optional[list] = None)->None:
        if price != None:
            if len(price) != 2:
                raise ValueError('Price List Has To Be Have 2 Values')
            
            elif (isinstance(price[0],str) and price[0] != '' and not price[0].isdigit()):
                raise ValueError('Price List "From" Is Not Digit')
            
            elif (isinstance(price[1],str) and price[1] != '' and not price[1].isdigit()):
                raise ValueError('Price List "To" Is Not Digit')

            self._filter['price'] = price
        
        else:
            self._filter['price'] = ['','']
        
        if rooms != None:
            rooms = list(map(str, rooms))

            for r in rooms:
                if str(r) not in ['1','2','3','4','5','5+','free','studio']:
                    raise ValueError('Rooms List Has Undefined Value : "%s"' % r)
            
            self._filter['rooms'] = rooms
        else:
            self._filter['rooms'] = []
        
    
    def setCity(self, city:str)->None:
        if city not in self.cities:
            raise ValueError('Undefined City %s' %city) 

        self._city = city
    
    def setAsync(self, _as:bool = True)->None:
        self.isAsync = _as


    def form(self):
        if not self._filter:
            raise ValueError('Filter Has Not Been Defined')
        if not self._city:
            raise ValueError('City Has Not Been Defined')
        
        if self.isAsync:
            self._thread = Thread(target = self._run)
            self._thread.name = 'SeleniumThread'
            self._thread.daemon = True
            self._thread.start()

        else:
            return self._run()
    
    def stop(self):
        for dr in self._drivers:
            dr.quit()
            
        if self._thread != None and self._thread.is_alive():
            self._thread.join()
        
    def _run(self)->dict:   
        urls = {
                'avito':self.get_avito_url(),
                'cian':self.get_cian_url()
            }
        
        
        if self._callback != None:
            self._callback(urls)

        return urls





class Parser():
    def __init__(self, callback:Callable = None):
        self.callback = callback
        self.isRunning = False
        self.timeout = 60
        self._flag = Event()
        
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1))
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
        }
        # with open('/Users/bimba/Desktop/KivyApp/assets/json/xpath.json') as f_in:
        #     self.xpath = json.load(f_in)

        #     f_in.close()

        self.cards = {
            # k:{} for k in self.xpath
        }

        self.links = {
            # k:'' for k in self.xpath
        }

        self.pagination = {
            # k:{'content':[],'current':''} for k in self.xpath
        }

        self.status = {
            # k:'NONE' for k in self.xpath
        }

        self.xpath = {

        }
    def set_callback(self, callback:Callable = None):
        self.callback = callback

    def inflate(self, name:str, xpath:dict):
        self.xpath[name] = xpath
        self.cards[name] = {}
        self.links[name] = ''
        self.pagination[name] = {'content':[],'current':''}
        
        if len(xpath) > 0:
            self.status[name] = 'NONE'
        else:
            self.status[name] = 'XPATH_ERROR'

    
    def apply_url(self, name:str, url:str):
        self.links[name] = url

    def get(self, key:str)->dict:
        if self.callback:
            self.callback({'status':'GET', 'url':self.links[key],'platform':key})

        self.status[key] = 'GET'
        
        resp = self.session.get(self.links[key], headers = self.headers, stream=True, verify=False, allow_redirects=True)
        
        if resp.status_code == 200:
            tree = html.fromstring(
                    resp.content,
                    parser = etree.HTMLParser(encoding='utf-8')
                )

            
            if tree.xpath(self.xpath[key]['count']):
                if self.callback:
                    self.callback({'status':'PARSE', 'url':self.links[key], 'platform':key})

                self.status[key] = 'PARSE'
                
                cards = {
                    'https://www.avito.ru%s' % el.xpath(self.xpath[key]['link'])[0] if key == 'avito' else el.xpath(self.xpath[key]['link'])[0]:
                    {
                            'img_sources':el.xpath(self.xpath[key]['cards']['img']),
                            'title':' '.join(el.xpath(self.xpath[key]['cards']['title'])),
                            
                            'subway_name':' '.join(el.xpath(self.xpath[key]['cards']['subway_name'])),
                            'subway_time':' '.join(el.xpath(self.xpath[key]['cards']['subway_time'])),
                            
                            'address':' '.join(el.xpath(self.xpath[key]['cards']['address'])),
                            'price':'%s ₽/мес.' % '{:,}'.format(int(''.join(ch for ch in el.xpath(self.xpath[key]['cards']['price'])[0] if ch.isdigit()))).replace(',',' '),
                            'meta':' '.join(el.xpath(self.xpath[key]['cards']['meta'])),
                            'description':' '.join(el.xpath(self.xpath[key]['cards']['description'])),
                            
                            'time':' '.join(el.xpath(self.xpath[key]['cards']['time'])),

                            'platform':key
                        } for el in tree.xpath(self.xpath[key]['content'])}
                
                if len(tree.xpath(self.xpath[key]['pagination']['content'])) > 1:
                    pagination = {
                        'content':tree.xpath(self.xpath[key]['pagination']['content']),
                        'current':tree.xpath(self.xpath[key]['pagination']['current'])[0]
                    }
                else:
                    pagination = None
                
                return {'status':'ok', 'cards':cards, 'pagination':pagination}
            else:
                return {'status':'empty'}

        else:
            if self.callback:
                self.callback({'status':'CODE', 'code':resp.status_code})    
            
            return {'status':'error'}
        
        # except Exception as e:
        #     if self.callback:
        #         self.callback({'status':'ERROR','error':e})
            
        #     return {'status':'error','error':e}


        

    def compare(self, a:dict, b:dict) -> dict:
        return {
            'new_cards':{k:a[k] for k in a if k not in b},
            'remove_cards':[k for k in b if k not in a]
        }

    def page(self, name, page):
        if self.callback:
            self.callback({'status':'PAGE','page':page,'platform':name})

        if self.links[name]:
            if self.pagination[name]['content'].index(page) >= 0 and self.pagination[name]['content'].index(page) < len(self.pagination[name]['content']) - 1:
                try:
                    self.links[name] = self.links[name].replace(
                        re.findall('[&?]p=[0-9]+', self.links[name])[0],
                        '&p={}'.format(page)
                    )
                except IndexError:
                    self.links[name] = self.links[name] + '&p={}'.format(page)
            self.refresh()

            return True
        return False

    def index(self):
        data = {}

        for key in self.xpath:
            if self.status[key] == 'XPATH_ERROR':
                break
            
            if self.links[key]:

                resp = self.get(key)
                
                if resp['status'] == 'ok':

                    data[key] = self.compare(resp['cards'], self.cards[key])
                    data[key]['pagination'] = resp['pagination']
                    data[key]['cards'] = resp['cards']

                    self.cards[key] = resp['cards']
                    self.pagination[key] = resp['pagination']

                    if self.callback:
                        self.callback({
                            'status':'DATA',
                            'platform':key, 
                            'data':{
                                    'cards':resp['cards'],
                                    'pagination':resp['pagination']
                                }
                            })
                        
                elif resp['status'] == 'empty':
                    self.callback({'status':'NO_CARDS', 'platform':key})
                    
                self.status[key] = 'WAIT'

                    

        return data
            

    def event(self, run:bool = True, time:str = ''):
        if run:
            self.index()
        else:
            if self.callback:
                self.callback({'status':"WAIT",'time':time})

    def run(self, handler:Callable = None, timeout:float = 60, once:bool = False):
        self.isRunning = True

        if self.callback:
            self.callback({'status':'RUN','timeout':timeout,'once':once})

        self._flag = Event()

        self._thread = ParserThread(
                event = self.event, 
                handler = handler, 
                flag = self._flag, 
                timeout = timeout,
                once = once
            )
        self._thread.daemon = True
        self._thread.start()

    def refresh(self):
        if self.callback:
            self.callback({'status':'REFRESH'})

        self.stop()
        self.run(
            handler = self._thread.handler, 
            timeout = self._thread.timeout, 
            once = self._thread.once)

    def stop(self):
        if self._flag:
            self._flag.set()


class ParserThread(Thread):
    def __init__(self, event:Callable, flag:Event, handler:Callable, timeout:float, once:bool = False, callback:Callable = None):
        Thread.__init__(self)

        self.event = event 
        self.timeout = timeout 
        self.handler = handler
        self.flag = flag
        self.once = once
        self.callback = callback
        self.timer = self.timeout

        
    def run(self):
        while True:
            if self.timer >= self.timeout:
                self.timer = 0
                self.event(run = True, time = None)
            else:
                self.timer += 1
                self.event(run = False, time = self.timer)

            
            if self.flag.wait(1) or self.once:
                return

def write_to_file(data, exit = False):
    with open('/Users/bimba/Desktop/KivyApp/assets/json/test_data.json','w') as f_in:
        json.dump(data, f_in, indent=4)

        f_in.close()

        if (exit):
            os.kill(os.getpid(),signal.SIGKILL)

def cc(data):
    print(data)

    sys.exit()
if __name__ == '__main__':
    former = UrlFormer(headless=False) 
    former.setCity('Абаза')
    former.setFilter(price=['',''],rooms=[])
    
    former.setAsync(True)
    former.connect(cc)
    former.form()

    
