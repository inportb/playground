import os

class Command():
	'list directory contents'
	def __call__(self,argv,stdin=None):
		if len(argv) < 2:
			argv.append('.')
		res = {}
		for arg in argv[1:]:
			if os.path.isdir(arg):
				res[arg] = [self.statpath(fn,os.path.join(arg,fn)) for fn in os.listdir(arg)]
			else:
				res[arg] = self.statpath(arg,arg)
		return res
	def statpath(self,basename,path):
		stat = os.stat(path)
		stat = dict((k[3:],getattr(stat,k)) for k in dir(stat) if k.startswith('st_'))
		return {
			'name':	basename,
			'stat':	stat,
			'link':	os.path.realpath(path) if os.path.islink(path) else None
			}
