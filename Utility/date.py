from datetime import datetime

class Date:
	WEEKDAY = {
		0:'Понедельник',
		1:'Вторник',
		2:'Среда',
		3:'Четверг',
		4:'Пятница',
		5:'Суббота',
		6:'Воскресенье'
	}

	MONTH = {
		'January' : 'Января',
		'February' : 'Февраля',
		'March' : 'Марта',
		'April' : 'Апреля',
		'May' :'Мая',
		'June' : 'Июня',
		'July' : 'Июля',
		'August' : 'Августа',
		'September' : 'Сентября',
		'October' : 'Октября',
		'November' : 'Ноября',
		'December' : 'Декабря'
	}


	
	def date(timestamp = None):
		if timestamp:
			dt = datetime.fromtimestamp(timestamp)
		else:
			dt = datetime.now()

		return f'{Date.WEEKDAY[dt.weekday()]}, {dt.day} {Date.MONTH[dt.strftime("%B")]} {dt.year}'


	def time(timestamp = None):
		if timestamp:
			dt = datetime.fromtimestamp(timestamp)
		else:
			dt = datetime.now()

		return '{h}:{z}{m}'.format(h = dt.hour, m = dt.minute, z = 0 if dt.minute < 10 else '')

	def compare(d1:str, d2:str)->bool:
		d1 = d1.split(' ')
		d2 = d2.split(' ')
		
		if int(d1[3]) != int(d2[3]):
			return int(d1[3]) > int(d2[3])
		if d1[2] != d2[2]:
			
			for month in Date.MONTH.values():
				if month == d1[2].lower():return False
				elif month == d2[2].lower():return True

		if d1[1] != d2[1]:
			return int(d1[1]) > int(d2[1])
		
		return True
	
	def compare_time(t1:str, t2:str):
		t1 = t1.split(':')
		t2 = t2.split(':')

		if int(t1[0]) != int(t2[0]):
			return int(t1[0]) > int(t2[0])
		return t1[1] > t2[1]


