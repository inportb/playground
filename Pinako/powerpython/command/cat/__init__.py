class Command():
	'concatenate files and print on the standard output'
	def __call__(self,argv,stdin=None):
		return '\n'.join(self.catfile(fn) for fn in argv[1:])
	def catfile(self,fn):
		try:
			return open(fn,'rb').read()
		except IOError:
			return ''
