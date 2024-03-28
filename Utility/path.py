import os,sys

class Path:
	_basedir = os.path.normpath(os.path.dirname(__file__) + os.sep + os.pardir)


	def set_basedir(basedir):
		try:
			Path._basedir = sys._MEIPASS
		except Exception:
			Path._basedir = os.path.abspath(".")


	def database(filename = 'renthelper.db'):
		return os.path.join(Path._basedir, 'assets/data','renthelper.db')
	
	def image(filename):
		return os.path.join(Path._basedir, 'assets/images', filename)
	
	def json(filename):
		return os.path.join(Path._basedir, 'assets/json', filename)

	def icon(filename):
		return os.path.join(Path._basedir, 'assets/images/icons', filename)

	def font(filename):
		return os.path.join(Path._basedir, 'assets/fonts', filename)
	

