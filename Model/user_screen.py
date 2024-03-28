from Utility.firebase import Firebase
from Utility.db import DataBase
from Utility.observer import Observer

import logging
import platform


class UserScreenModel:
    def __init__(self):
        self.observers = []
        self.fb = Firebase()
        self.user = {
            'authorized':False,
            'email':'',
            'displayName':'',
        }
        
    
    def setUser(self, user):
        self.user = user
        
        self.notify_observer(
            Observer.ObserverEvent(Observer.ObserverEvent.AUTHENTICATION), user
        )

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)
    
            
    def notify_observer(self, t:Observer.ObserverEvent = None, data:dict = {}):
        for observer in self.observers:
            observer.model_is_changed(t, data)