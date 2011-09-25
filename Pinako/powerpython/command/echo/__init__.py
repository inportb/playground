class Command():
	'display a line of text'
	def __call__(self,argv,stdin=None):
		return ' '.join(argv[1:])
