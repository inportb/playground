import os

class Command():
	'return name of current/working directory'
	def __call__(self,argv,stdin=None):
		return os.getcwd()
