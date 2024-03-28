# -*- coding: utf-8 -*-

from collections.abc import Callable, Iterable, Mapping
from typing import Any, Optional
import pyrebase 
import json
import threading
import time
from requests.exceptions import HTTPError
from Utility.path import Path

class FirebaseDataBase:
    def __init__(self, firebase) -> None:
        self.db = firebase.database()

    def path(self, uid = None):
        return self.db.child('cards').child(uid) if uid else self.db.child('cards')

    def set(self, data:dict, token:str, uid:str)->dict:
        try:
            self.path(uid).set(data=data, token=token)

            return {
                'status':'ok'
            }
        except HTTPError as e:
            js_er = json.loads(e.strerror)

            return {
                    'status':'error', 
                    'error': js_er['error']
                }
                
    def push(self, id:str, data:dict, token:str, uid:str) -> dict:
        try:
            self.path(uid).child(self.convert(id)).set(data = data, token = token)

            return {
                'status':'ok',
            }
        except HTTPError as e:
            js_er = json.loads(e.strerror)

            return {
                'status':'ok',
                'error':js_er['error']
            }
    
    def convert(self, string, invert = False):
        rg = [['/','|'], ['.',';']]
        i, j = 1 if invert else 0, 0 if invert else 1

        for r in rg:
            string = string.replace(r[i],r[j])
            
        return string
    
    def remove(self, id, token, uid):
        self.path(uid).child(self.convert(id)).remove(token = token)

    def get_data(self, token, uid):
        try:
            data = self.db.child('cards').child(uid).get(token=token)
            return {
                'status':'ok',
                'data':{
                    self.convert(row.key(), invert = True):{a0:a1
                                                             for a0,a1 in row.val().items()} for row in data.each() 
                } if data.each() != None else {}
            }
        
        except HTTPError as e:
            js_er = json.loads(e.strerror)

            return {
                'status':'error',
                'error':js_er['error']
            }

    def set_user_info(self, token, uid,**kwargs):
        try:
            self.db.child('users').child(uid).update(kwargs, token=token)

            return {
                'status':'ok'
            }
        except Exception as e:
            js_er = json.loads(e.strerror)

            return {
                'status':'error',
                'error':js_er['error']
            }

    def get_user_info(self, token:str, uid:str)->dict:
        try:
            data = self.db.child('users').child(uid).get(token=token)

            return {
                'status':'ok',
                'data':data.val()
            }
        except HTTPError as e:
            js_er = json.loads(e.strerror)

            return {
                'status':'error',
                'error':js_er['error']
            }

class FirebaseUser:
    def __init__(self, firebase) -> None:
        self.auth = firebase.auth()
        
        
    def sign_up(self,email:str, password:str):
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
           

            return {
                'status':'ok',
                'id_token':user['idToken'],
                'refresh_token':user['refreshToken']
            }
         
            
        except HTTPError as e:
            return {
                'status':'error', 
                'error':[msg['message'] for msg in json.loads(e.strerror)['error']['errors']]
            }
        
    def sign_in(self,email:str, password:str):
        try:
            user = self.auth.sign_in_with_email_and_password(email=email, password=password)

            return {
                    'status':'ok',
                    'id_token':user['idToken'],
                    'refresh_token':user['refreshToken']
                }
        except HTTPError as e:
            return {
                'status':'error', 
                'error':[msg['message'] for msg in json.loads(e.strerror)['error']['errors']]
                }
    
    def logout(self):
        self.auth.current_user = None
    def token(self)->str:
        return self.auth.current_user['idToken'] if self.authorized() else ''
    def uid(self)->str:
        return self.auth.current_user['localId']if self.authorized() else ''
    def authorized(self)->bool:
        return self.auth.current_user != None

class SingleShot(threading.Thread):
    def __init__(self, target:Callable, delay:float = 5, finished:Optional[Callable] = None,args:list = []) -> None:
        threading.Thread.__init__(self)
        

        self.target = target
        self.delay = delay
        self.args = args
        self.finished = finished
        self.daemon = False
        self._is_started = False
        self._is_corrupted = False
        self._time = 0

    
    def is_started(self)->bool:
        return self._is_started
    
    def start(self) -> None:
        return super().start()
    
    def stop(self):
        self._is_corrupted = True
    def refresh(self):
        if not self.is_started():
            self._time = 0

    def run(self) -> None:
        while self._time < self.delay:
            time.sleep(1)
            self._time += 1

        if not self._is_corrupted:
            self._is_started = True

            for kwargs in self.args:
                self.target(**kwargs)

            self._is_started = False
            if self.finished:
                
                self.finished()

class Firebase():
    
    def __init__(self):
        self._listener = None

        self._threads = []

        try:
            config = json.load(open(Path.json('firebase_config.json')))

            self.instance = pyrebase.initialize_app(config)

            self.user = FirebaseUser(firebase=self.instance)
            self.db = FirebaseDataBase(firebase=self.instance)

        except FileNotFoundError as e:
            return
    
    def sign_in(self, email, password):
        res = self.user.sign_in(email=email, password=password)

        return res['status'] == 'ok'
    
    def sign_up(self, email, password):
        res = self.user.sign_up(email=email, password=password)

        return res['status'] == 'ok'

    
    def _shot(self, target:Callable, delay:int = 5,**kwargs):
        if self.authorized():
            def _do_shot()->bool:
                for _th in reversed(self._threads):
                    if not _th.is_started() and _th.is_alive() and target == _th.target:
                        for _th_kwargs in _th.args:
                            if _th_kwargs['id'] == id:
                                _th_kwargs.update(kwargs)
                                _th.refresh()

                                return False
                        kwargs.update({'uid':self.user.uid(),'token':self.user.token()})

                        _th.args.append(kwargs)
                        _th.refresh()

                        return False
                return True


            if _do_shot(): 
                kwargs.update({'uid':self.user.uid(),'token':self.user.token()})

                single_shot = SingleShot(
                    target = target, 
                    delay = delay, 
                    args = [kwargs])
                print(single_shot.args, kwargs)
                single_shot.finished = lambda instance = single_shot : self._threads.remove(instance)
                single_shot.start()

                self._threads.append(single_shot)

    def push(self, id:str, data:dict, delay:int = 0)->None:
        self._shot(target = self.db.push, id = id, data = data)

    def remove(self, id:str):
        
        self._shot(target=self.db.remove, id = id)

    def set_stream(self, handler:callable):
        if self.authorized():
            self._listener = self.db.path(self.user.uid()).stream(handler, token = self.user.token())
    def stop_stream(self):
        if self._listener:
            self._listener.close()
            
        for _th in self._threads:
            _th.join()
    def get_data(self):
        if self.user.authorized():
            res = self.db.get_data(
                token=self.user.token(), 
                uid = self.user.uid())

            if res['status'] == 'ok':
                return res['data']
        
        return False

    def authorized(self)->bool:
        return self.user.authorized()
    def logout(self):
        self.user.logout()
        
    def set_user_info(self, **kwargs):
        if self.user.authorized():
            self.db.set_user_info(token=self.user.token(), uid = self.user.uid(), **kwargs)

    def get_user_info(self)->dict:
        if self.user.authorized():
            return {
                'email':self.user.auth.current_user['email'],
                'displayName':self.user.auth.current_user['displayName']
            }
            
        return None



