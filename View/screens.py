from Model.content_screen import ContentScreenModel
from Controller.content_screen import ContentScreenController

from Model.history_screen import HistoryScreenModel
from Controller.history_screen import HistoryScreenController

from Model.favourite_screen import FavouriteScreenModel
from Controller.favourite_screen import FavouriteScreenController

from Model.user_screen import UserScreenModel
from Controller.user_screen import UserScreenContoller

screens = {
	'content screen':{
		'controller':ContentScreenController,
		'model':ContentScreenModel,
		'icon':'ad.png',
        'name':'Объявления'
	},
	'history screen':{
		'model':HistoryScreenModel,
		'controller':HistoryScreenController,
		'icon':'history.png',
        'name':'Иcтория'
	},
	'favourite screen':{
		'model':FavouriteScreenModel,
		'controller':FavouriteScreenController,
		'icon':'favourite_screen.png',
        'name':'Любимое'
	},
    'user screen':{
        'model':UserScreenModel,
        'controller':UserScreenContoller,
        'icon':'user.png',
        'name':''
	}
}