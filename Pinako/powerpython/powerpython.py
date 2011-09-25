#!/usr/bin/env python

try:
	import readline
except ImportError:
	print 'please get pyreadline from <http://pypi.python.org/pypi/pyreadline>'
	raise

import logging, atexit, sqlite3, shlex, glob, yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s\t- %(message)s'))
logger.addHandler(ch)

class Command(object):
	pass

class Object(yaml.YAMLObject):
	yaml_loader = yaml.SafeLoader
	yaml_tag = u'!Object'

class Shell(object):
	def __init__(self,cmddir=None):
		if cmddir is None:
			fp,path,desc = imp.find_module('command')
			if fp is None:
				cmddir = path
			else:
				fp.close()
				raise ImportError
		self.db = db = sqlite3.connect(':memory:')
		db.row_factory = sqlite3.Row
		self.cur = cur = db.cursor()
		cur.execute('CREATE TABLE cmd (key TEXT, doc TEXT);')
		cur.execute('CREATE UNIQUE INDEX cmd_key ON cmd (key)')
		self.cmddir = cmddir
		self.command = cmddict = {}
		for m in os.listdir(cmddir):
			moddir = os.path.join(cmddir,m)
			modfile = os.path.join(moddir,'__init__.py')
			if os.path.isdir(moddir) and os.path.isfile(modfile):
				fp,path,desc = imp.find_module(m,[cmddir])
				try:
					mod = imp.load_module('command.'+m,fp,path,desc)
					try:
						doc = mod.__doc__
					except AttributeError:
						doc = ''
					cur.execute('INSERT INTO cmd (key,doc) VALUES (?,?)',(m,doc))
					cmddict[m] = mod.Command
				finally:
					if fp is not None:
						fp.close()
	def execute(self,text):
		argv = shlex.split(text.lstrip())
		if len(argv) > 0 and len(argv[0]) > 0:
			self.cur.execute('SELECT key FROM cmd WHERE key=? LIMIT 1',(argv[0],))
			try:
				cmd = self.cur.fetchone()[0]
			except TypeError:
				print argv[0]+': command not found'
				return
			try:
				res = self.command[cmd]()(list(self.expand(argv)),None)
				if res is not None:
					if isinstance(res,(basestring,int,float,bool)):
						print res
					else:
						print yaml.dump(res).rstrip()
			except:
				logger.exception(cmd)
	def expand(self,argv):
		for arg in argv:
			if '*' in arg or '?' in arg:
				g = glob.glob(arg)
				if len(g) > 0:
					for i in g:
						yield i
					continue
			yield arg
	def complete(self,text,state):
		text = text.replace('%','\\%').replace('_','\\_')
		self.cur.execute('SELECT key FROM cmd WHERE key LIKE ? ORDER BY key LIMIT 1 OFFSET ?',(text+'%',state))
		try:
			return self.cur.fetchone()[0]
		except TypeError:
			return

if __name__ == '__main__':
	import os, imp, platform, getpass
	shell = Shell()
	try:
		readline.read_init_file('dot-ppyrc')
	except IOError:
		try:
			readline.read_init_file('/etc/ppy.ppyrc')
		except IOError:
			pass
	try:
		readline.read_history_file('dot-ppyhist')
	except IOError:
		pass
	atexit.register(readline.write_history_file,'dot-ppyhist')
	readline.set_completer(shell.complete)
	readline.parse_and_bind('tab: complete')
	try:
		while True:
			try:
				shell.execute(raw_input('%s@%s:%s> '%(getpass.getuser(),platform.node(),os.getcwd())).strip())
			except KeyboardInterrupt:
				print '^C'
	except EOFError:
		print
