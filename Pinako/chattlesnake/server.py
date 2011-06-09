#!/usr/bin/env python
## Simple IRC server based on gevent
##
## Copyright (C) 2011 by Jiang Yio <http://inportb.com/>
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

import logging, re, random, time, datetime, fnmatch, sqlite3, gevent
from collections import deque
from itertools import izip
from binascii import hexlify
from fnmatch import fnmatchcase
from heapq import heappush, heappop
from gevent import Greenlet, Timeout, GreenletExit, socket, dns, sleep
from gevent.event import Event, AsyncResult
from gevent.server import StreamServer
from gevent.queue import Queue

from jsonrpc import JSONPeer
from jsoncluster import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s\t- %(message)s'))
logger.addHandler(ch)

RPL_WELCOME		= 001
RPL_NAMREPLY	= 353
RPL_ENDOFNAMES	= 366

class RPCError(BaseException):
	def __init__(self,code,message,data=None):
		self.value = {'code':code,'message':message}
		if data is not None:
			self.value['data'] = data
	def __str__(self):
		return json.dumps(self.value,separators=(',',':'))

class IRCError(BaseException):
	def __init__(self,code,message):
		self.code = code
		self.message = message
IRCError.NoSuchNick			= IRCError(401,'no such nick')
IRCError.NoSuchChannel		= IRCError(403,'no such channel')
IRCError.CannotSendToChan	= IRCError(404,'cannot send to chan')
IRCError.ErroneousNickname	= IRCError(432,'erroneous nickname')
IRCError.NicknameInUse		= IRCError(433,'nickname in use')
IRCError.NotRegistered		= IRCError(451,'not registered')
IRCError.NeedMoreParams		= IRCError(461,'need more params')
IRCError.AlreadyRegistered	= IRCError(462,'already registered')
IRCError.BannedFromChan		= IRCError(474,'banned from chan')

class IRCChannel(object):
	len_chan = 50
	len_topic = 390
	re_chan = re.compile(r'^(?:#|\+)([0-9A-Za-z-_#])+$')
	mode_simple = 'CFLMPQcgimnprstz'
	mode_param = 'kljfI'
	mode_list = 'beqaohv'
	mode_param_all = mode_param+mode_list
	def __init__(self,server,name):
		self.started = time.time()
		self.started_str = datetime.datetime.utcfromtimestamp(self.started).isoformat()
		self.server = server
		self.serverprefix = server.prefix
		self.name = name
		self.topic_data = None
		self.client = set()
		self.quiet = set()
		self.namreply_dict = {}
		self.namreply = ''
		self.db = db = sqlite3.connect(':memory:')
		self.cur = cur = db.cursor()
		cur.execute('CREATE TABLE mode (key TEXT, value TEXT, setter TEXT, ctime FLOAT)')
		cur.execute('CREATE INDEX mode_key ON mode (key)')
		cur.execute('CREATE INDEX mode_value ON mode (value)')
		cur.execute('CREATE UNIQUE INDEX mode_idx ON mode (key,value)')
	def send(self,src,msg,exclude=None):
		for c in self.client:
			if c is not exclude:
				c.send(src,msg)
	def join(self,client):
		name = self.name
		if client not in self.client:
			prefix = client.prefix.lower()
			exempt = None
			cur = self.cur
			cur.execute('SELECT key FROM mode WHERE key=? AND ? GLOB value LIMIT 1',('b',prefix))
			if cur.fetchone() is not None:
				cur.execute('SELECT key FROM mode WHERE key=? AND ? GLOB value LIMIT 1',('e',prefix))
				if cur.fetchone() is None:
					raise IRCError.BannedFromChan
				exempt = True
			self.client.add(client)
			cur.execute('SELECT key FROM mode WHERE key=? AND ? GLOB value LIMIT 1',('q',prefix))
			if cur.fetchone() is not None:
				if not exempt:
					cur.execute('SELECT key FROM mode WHERE key=? AND ? GLOB value LIMIT 1',('e',prefix))
					if cur.fetchone() is not None:
						exempt = True
				if not exempt:
					self.quiet.add(client)
			if name[0] == '#' and len(self.client) == 1:
				cur.execute('INSERT OR IGNORE INTO mode (key,value,setter,ctime) VALUES (?,?,?,?)',('o',client.name.lower(),self.serverprefix,self.started))
				client.channel[self] = set()
			else:
				client.channel[self] = set()
			msg = 'JOIN :'+name
			for c in self.client:
				c.send(client.prefix,msg)
			if self.topic_data is not None:
				client.send(self.serverprefix,'332 %s %s :%s'%(client.name,name,self.topic_data[0]))
				client.send(self.serverprefix,'333 %s %s %s %d'%(client.name,name,self.topic_data[1],self.topic_data[2]))
				#client.send(self.topicsetter,'TOPIC %s :%s'%(name,self.topictext))
			self.namreply_set(client)
			return True
		return False
	def part(self,client,msg):
		if client in self.client:
			if msg is not None:
				msg = 'PART %s :%s'%(self.name,msg)
				for c in self.client:
					c.send(client.prefix,msg)
			del client.channel[self]
			del self.client[client]
			self.quiet.discard(client)
			self.namreply_res(client.name)
			return True
		return False
	def mode(self,src,key,*args):	# FIXME: check privilege
		mode_simple = self.mode_simple
		mode_param = self.mode_param
		mode_ban = self.mode_ban
		value = reversed(args).next
		ki = 0
		vi = 0
		now = time.time()
		op = None
		voice = set()
		ban = set()
		unban = set()
		try:
			for k in key:
				ki += 1
				if k == '+':
					op = True
				elif k == '-':
					op = False
				elif op is None:
					pass	# FIXME: allow getting ban lists
				elif k in mode_simple:
					if op is True:
						cur.execute('INSERT OR IGNORE INTO mode (key,value,setter,ctime) VALUES (?,?,?,?)',(k,'',src,now))
					else:
						cur.execute('DELETE FROM mode WHERE key=?',(k,))
				elif k in mode_param:
					if op is True:
						v = value()
						cur.execute('DELETE FROM mode WHERE key=?',(k,))
						cur.execute('INSERT OR IGNORE INTO mode (key,value,setter,ctime) VALUES (?,?,?,?)',(k,v,src,now))
					else:
						cur.execute('DELETE FROM mode WHERE key=?',(k,))
					vi += 1
				elif k in mode_list:	# FIXME: privileged/exempted users ignore bans
					v = value().lower()
					ban = k in 'beq'
					if op is True:
						cur.execute('INSERT OR IGNORE INTO mode (key,value,setter,ctime) VALUES (?,?,?,?)',(k,v,src,now))
						if k in 'bq':
							for c in self.client:
								if fnmatchcase(c.prefix,v):
									self.quiet.add(c)
						elif k in 'aohv':	# FIXME: move this out of the loop
							for c in self.client:
								if c.name.lower() == v:
									self.namreply_set(c)
									break
					else:
						cur.execute('DELETE FROM mode WHERE key=? AND value=?',(k,v))
						if k in 'bq':	# FIXME: move this out of the loop
							ignore = set(self.client)
							for c in self.client:
								cur.execute('SELECT key FROM mode WHERE key IN (?,?) AND ? GLOB value LIMIT 1',('b','q',prefix))
								if cur.fetchone() is not None:
									ignore.discard(c)
							for c in ignore:
								self.quiet.discard(c)
						elif k in 'aohv':	# FIXME: move this out of the loop
							for c in self.client:
								if c.name.lower() == v:
									self.namreply_set(c)
									break
					vi += 1
		except StopIteration:
			ki -= 1
		msg = 'MODE %s %s %s'%(self.name,key[:ki],' '.join(args[:vi]))
		for c in self.client:
			c.send(src,msg)
	def namreply_set(self,client):
		name = client.name
		self.cur.execute('SELECT key FROM mode WHERE value=?',(name,))
		modeset = set(row[0] for row in self.cur)
		if 'a' in modeset:
			self.namreply_dict[name] = '&'+name
		elif 'o' in modeset:
			self.namreply_dict[name] = '@'+name
		elif 'h' in modeset:
			self.namreply_dict[name] = '%'+name
		elif 'v' in modeset:
			self.namreply_dict[name] = '+'+name
		else:
			self.namreply_dict[name] = name
		self.namreply = ' '.join(self.namreply_dict.itervalues())
	def namreply_res(self,name):
		try:
			del self.namreply_dict[name]
		except KeyError:
			pass
		else:
			self.namreply = ' '.join(self.namreply_dict.itervalues())

class IRCClient(Greenlet):
	len_nick = len_user = 16
	re_nick = re_user = re.compile(r'[^0-9A-Za-z\[\]{}_^`\-\|\\]')
	mode_simple = 'DOQRSZaghilopswz'
	mode_param = ''
	makeprefix = staticmethod(lambda name,username,hostname: '%s!%s@%s'%(name,username,hostname))
	def __init__(self,server,sock,name,username,hostname,realname,usermode,password='',account=None,checkpoint=None):
		Greenlet.__init__(self)
		self.server = server
		self.sock = sock
		self.name = name
		self.username = username
		self.hostname = hostname
		self.realname = realname
		self.usermode = usermode
		self.checkpoint = checkpoint
		self.prefix = self.makeprefix(name,username,hostname)
		self.channel = {}
		self.sendq = Queue()
		self.quit = None
		self.serverprefix = server.prefix
		self.welcome()
	def _run(self):
		sendall = self.sock.sendall
		get = self.sendq.get
		try:
			if self.checkpoint is not None:
				self.checkpoint.wait()
			while True:
				sendall(get())
		except IOError:
			pass
	def sendraw(self,msg):
		self.sendq.put(msg)
	def send(self,src,msg):
		self.sendq.put(':%s %s\r\n'%(src,msg))
	def welcome(self):	# http://www.alien.net.au/irc/irc2numerics.html
		# FIXME: dummy values
		send = self.send
		server = self.server
		name = self.name
		networkname = server.networkname
		serverprefix = self.serverprefix
		software = 'chattlesnake-dev'
		send(serverprefix,'NICK :'+name)
		send(serverprefix,'001 %s :Welcome to the %s Network, %s'%(name,networkname,name))
		send(serverprefix,'002 %s :Your host is %s, running %s'%(name,serverprefix,software))
		send(serverprefix,'003 %s :This server was created %s'%(name,self.server.started_str))
		send(serverprefix,'004 %s %s %s %s %s %s %s %s %s'%(name,serverprefix,software,self.mode_simple+self.mode_param,IRCChannel.mode_simple+IRCChannel.mode_param_all,IRCChannel.mode_param_all,self.mode_param,server.mode_simple+server.mode_param,server.mode_param))
		send(serverprefix,'005 %s CHANTYPES=#+ PREFIX=(aov)&@+ NETWORK=%s STATUSMSG=&@+ CASEMAPPING=rfc1459 CHARSET=ascii NICKLEN=%d CHANNELLEN=%d TOPICLEN=%d :are supported by this server'%(name,networkname,self.len_nick,IRCChannel.len_chan,IRCChannel.len_topic))
		send(serverprefix,'251 %s :There are 0 users and 0 invisible on 0 servers'%name)
		send(serverprefix,'252 %s 0 :IRC Operators online'%name)
		send(serverprefix,'253 %s 0 :unknown connection(s)'%name)
		send(serverprefix,'254 %s %d :channels formed'%(name,len(server.data)-server.count_client))
		send(serverprefix,'255 %s :I have %d clients and %d servers'%(name,server.count_client,len(server.node.peer)))
		send(serverprefix,'265 %s %d 0 :Current local users %d, max 0'%(name,server.count_client,server.count_client))
		send(serverprefix,'266 %s %d 0 :Current global users %d, max 0'%(name,server.count_client,server.count_client))
		send(serverprefix,'250 %s :Highest connection count: 0 (0 clients) (0 connections received)'%name)
		send(serverprefix,'375 %s :- %s Message of the Day - '%(name,serverprefix))
		send(serverprefix,'372 %s :- Welcome to %s on the %s network.'%(name,serverprefix,networkname))
		send(serverprefix,'372 %s :- Thanks for playing!'%name)
		send(serverprefix,'376 %s :End of /MOTD command.'%name)
	def privmsg(self,target,msg,cmd='PRIVMSG'):
		if target[0] in '#+':
			try:
				c = self.server.data[target]
				if self not in c.client:
					raise IRCError.CannotSendToChan
			except KeyError:
				raise IRCError.NoSuchNick
			c.send(self.prefix,'%s %s :%s'%(cmd,target,msg),exclude=self)
		else:
			try:
				c = self.server.data[target.lower()]
			except KeyError:
				raise IRCError.NoSuchNick
			c.send(self.prefix,'%s %s :%s'%(cmd,target,msg))
	def do_nick(self,name,*args):
		l = len(name)
		if l < 1 or l > 16 or self.re_nick.search(name):
			raise IRCError.ErroneousNickname
		if name.lower() == self.name.lower():
			return
		server = self.server
		try:
			server.reserve_nick(name,self.len_nick)
		except KeyError:
			raise IRCError.NicknameInUse
		oldname = self.name
		self.name = name
		server.client_add(self)
		server.client_remove(oldname)
		msg = 'NICK :'+name
		for c in set(sum((tuple(channel.client) for channel in self.channel),())):
			c.send(self.prefix,msg)
		self.prefix = self.makeprefix(name,self.username,self.hostname)
	def do_user(self,username,usermode,ign,realname,*args):
		raise IRCError.AlreadyRegistered
	def do_pass(self,password,*args):
		pass
	def do_ping(self,*args):
		try:
			return 'PONG :%s'%args[0]
		except IndexError:
			return 'PONG :%s'%self.serverprefix
	def do_join(self,channel,password=None,*args):
		if password is None:
			channel = dict((cn,'') for cn in channel.split(','))
		else:
			channel = dict((cn,pw) for cn,pw in izip(channel.split(','),password.split(',')))
		server = self.server
		match = IRCChannel.re_chan.match
		namreply = []
		for cn,pw in channel.iteritems():
			if cn[0] not in '#+':
				continue
			try:
				c = server.data[cn]
			except KeyError:
				if len(cn) > 32 or not match(cn):
					#raise IRCError.NoSuchChannel
					continue
				c = IRCChannel(server,cn)
				server.data[cn] = c
			if c.join(self):
				namreply.append(cn)
		self.do_names(','.join(namreply))
	def do_names(self,channel=None,server=None,*args):
		server = self.server
		send = self.send
		name = self.name
		if channel is None:
			channellist = self.channel.iteritems()
		else:
			channellist = ((cn,server.data[cn]) for cn in channel.split(',') if cn[0] in '#+')
		for cn,c in channellist:
			if self in c.client:
				send(server.prefix,'%03d %s = %s %s'%(RPL_NAMREPLY,name,cn,c.namreply))
				send(server.prefix,'%03d %s %s :End of /NAMES list'%(RPL_ENDOFNAMES,name,cn))
	def do_privmsg(self,target,msg,*args):
		return self.privmsg(target,msg,'PRIVMSG')
	def do_notice(self,target,msg,*args):
		return self.privmsg(target,msg,'NOTICE')
	def do_part(self,channel,*args):
		args = ' '.join(args)
		server = self.server
		for cn in channel.split(','):
			if cn[0] not in '#+':
				continue
			try:
				c = server.data[cn]
			except KeyError:
				#raise IRCError.NoSuchChannel
				continue
			c.part(self,args)
	def do_quit(self,*args):
		self.quit = 'Quit: '+(' '.join(args))
		self.sock.close()
	@classmethod
	def accept(cls,server,sock,addr):
		logger.info('+client '+addr[0])
		sockfile = sock.makefile('rb')
		name = None
		username = None
		hostname = addr[0]
		realname = None
		usermode = 0
		password = ''
		client = None
		try:
			ip = socket.inet_aton(hostname)
			try:	# rDNS [and identd]
				with Timeout(4,False):
					hostname = dns.resolve_reverse(ip)[1]
			except (dns.DNSError,IndexError):
				pass
			while True:	# pre-registration loop
				line = sockfile.readline()[:512]
				if len(line) < 1:
					return
				line = line.rstrip('\r\n')
				try:
					arg,txt = line.split(':',1)
				except ValueError:
					arg = line.split()
				else:
					arg = arg.split()
					arg.append(txt)
				try:
					cmd = arg[0].lower()
				except IndexError:
					continue
				else:
					if cmd == 'pass':
						password = arg[1]
					elif cmd == 'nick':
						name = cls.re_nick.sub('',arg[1])
						if name[0] in '-0123456789':
							name = '_'+name
						name = server.reserve_nick(name[:cls.len_nick],cls.len_nick,rename=True)
					elif cmd == 'user':
						username = cls.re_user.sub('',arg[1])
						if username[0] in '-0123456789':
							username = '_'+username
						username = username[:cls.len_user]
						if len(username) < 1:
							username = ('~'+hexlify(ip).upper())[:cls.len_user-1]
						try:
							usermode = int(arg[2])
						except ValueError:
							usermode = 0
						realname = arg[3][:64]
					if None not in (name,username,realname):
						break
			client = cls(server,sock,name,username,hostname,realname,usermode,password)
			# FIXME: user mode
			client.start_later(0)
			server.client_add(client)
			send = client.send
			serverprefix = server.prefix
			logger.info('=client %s %s'%(addr[0],client.prefix))
			while True:	# post-registration loop
				line = sockfile.readline()[:512]
				if len(line) < 1:
					return
				line = line.rstrip('\r\n')
				try:
					arg,txt = line.split(':',1)
				except ValueError:
					arg = line.split()
				else:
					arg = arg.split()
					arg.append(txt)
				try:
					cmd = arg[0].lower()
					hnd = getattr(client,'do_'+cmd)
				except IndexError:
					logger.info('invalid command: %s'%line)
				except AttributeError:
					logger.info('no handler for command: %s'%line)
				else:
					try:
						res = hnd(*arg[1:])
					except IRCError,ex:
						send(serverprefix,'%03d :%s'%(ex.code,ex.message))
					except TypeError:
						logger.exception('wut')
						ex = IRCError.NeedMoreParams
						send(serverprefix,'%03d :%s'%(ex.code,ex.message))
					except GreenletExit:
						break
					except:
						logger.exception('an error occurred')
					else:
						if res is not None:
							send(serverprefix,res)
		finally:
			if client is not None:
				client.kill()
				msg = 'QUIT :Remote host closed the connection' if client.quit is None else ('QUIT :'+client.quit)
				target = set(sum((tuple(channel.client) for channel in client.channel),()))
				target.discard(client)
				for c in target:
					c.send(client.prefix,msg)
				for c in client.channel:
					c.part(client.prefix,None)
				server.client_remove(client.name)
			sockfile.close()
			sock.close()
			logger.info('-client '+addr[0])

class IRCClientProxy(object):
	makeprefix = staticmethod(lambda name,username,hostname: '%s!%s@%s'%(name,username,hostname))
	def __init__(self,server,via,serverprefix,name,username,hostname,realname,usermode):
		self.server = server
		self.via = via
		self.serverprefix = serverprefix
		self.name = name
		self.username = username
		self.hostname = hostname
		self.realname = realname
		self.usermode = usermode
		self.prefix = self.makeprefix(name,username,hostname)
	def send(self,src,msg):
		self.via.notify('client_send',self.serverprefix,self.name,':%s %s\r\n'%(src,msg))
	def sendraw(self,msg):
		self.via.notify('client_send',self.serverprefix,self.name,msg)

class IRCNodeHandler(ClusterHandler):
	def net_client_connect(self,(serverprefix,name,ctime)):
		return self.server.client_connect(serverprefix,name,ctime)
	def net_client_disconnect(self,(serverprefix,name)):
		return self.server.client_disconnect(serverprefix,name)
	def net_client_register(self,(serverprefix,name,username,hostname,realname,usermode)):
		return self.server.client_register(serverprefix,name,username,hostname,realname,usermode)
	def net_client_send(self,(serverprefix,name,msg)):
		return self.server.client_send(serverprefix,name,msg)

class IRCNode(NetworkNode):
	def __init__(self,server):
		NetworkNode.__init__(self,server.prefix)
		self.server = server

class IRCServer(object):
	mode_simple = ''
	mode_param = ''
	def __init__(self,networkname,servername,s2s,peer):
		self.started_str = datetime.datetime.utcnow().isoformat()
		self.networkname = networkname
		self.prefix = self.servername = servername
		self.db = db = sqlite3.connect(':memory:')
		self.cur = cur = db.cursor()
		cur.execute('CREATE TABLE client (name TEXT, nick TEXT, node TEXT, ctime FLOAT)')
		cur.execute('CREATE UNIQUE INDEX client_name on client (name)')
		cur.execute('CREATE UNIQUE INDEX client_nick on client (nick)')
		cur.execute('CREATE INDEX client_node on client (node)')
		self.data = {}
		self.count_client = 0
		self.count_channel = 0
		self.node = node = IRCNode(self)
		self.s2s = s2s = JSONPeer(s2s,handle=IRCNodeHandler,node=node)
		for s in peer:
			host,port = s.rsplit(':',1)
			s2s.connect((host,int(port)),handle=IRCNodeHandler,node=node)
		self.__setitem__ = self.data.__setitem__
		self.__getitem__ = self.data.__getitem__
		self.__delitem__ = self.data.__delitem__
	def reserve_nick(self,name,limit,rename=False):
		self.count_client += 1
		now = time.time()
		lname = name.lower()
		cur = self.cur
		cur.execute('SELECT COUNT(*) FROM client WHERE name=?',(lname,))
		if cur.fetchone()[0] < 1:
			self.client_connect(self.prefix,name,now)
			return name
		if not rename:
			raise KeyError
		lname = 'guest'
		while True:
			count = random.randint(10000,99999)
			cname = lname+str(count)
			cur.execute('SELECT COUNT(*) FROM client WHERE name=?',(cname,))
			if cur.fetchone()[0] < 1:
				name = 'Guest'+str(count)
				self.client_connect(self.prefix,name,now)
				return name
	def client_add(self,c):
		lname = c.name.lower()
		if self.data[lname] is None:
			self.data[lname] = c
		else:
			raise KeyError
		self.node.notify('client_register',(self.prefix,c.name,c.username,c.hostname,c.realname,c.usermode))
	def client_connect(self,serverprefix,name,ctime):
		lname = name.lower()
		now = time.time()
		self.data[lname] = None
		self.cur.execute('INSERT INTO client (name,nick,node,ctime) VALUES (?,?,?,?)',(name.lower(),name,serverprefix,ctime))
		self.node.notify('client_connect',(serverprefix,name,ctime))
		print '+',serverprefix,name,ctime
	def client_register(self,serverprefix,name,username,hostname,realname,usermode,exclude=None):
		if serverprefix != self.prefix:
			self.data[name.lower()] = IRCClientProxy(self,self.peer[serverprefix],serverprefix,name,username,hostname,realname,usermode)
	def client_remove(self,name):
		self.node.notify('client_disconnect',(self.prefix,name))
		self.client_disconnect(self.prefix,name)
	def client_disconnect(self,serverprefix,name,exclude=None):
		lname = name.lower()
		try:
			c = self.data.pop(lname)
			if serverprefix == self.prefix and isinstance(c,IRCClient):
				self.count_client -= 1
		except KeyError:
			pass
		self.cur.execute('DELETE FROM client WHERE node=? AND name=?',(serverprefix,lname))
		print '-',serverprefix,name
	def client_send(self,serverprefix,name,msg,exclude=None):
		if serverprefix == self.prefix:
			try:
				self.data[name.lower()].sendraw(msg)
			except KeyError:
				pass
		else:
			self.node.notify('client_send',(serverprefix,name,msg))
	def serve(self,listener,backlog=None,spawn='default'):
		return StreamServer(listener,handle=self.handle,backlog=backlog,spawn=spawn)
	def handle(self,sock,addr):
		IRCClient.accept(self,sock,addr)

if __name__ == '__main__':
	# usage:
	#  server.py <c2s port> <s2s port> [s2s peer, ...]
	import sys, os
	servername = sys.argv[2]+u'.chattlesnake.localhost'
	ircd = IRCServer('Chattlesnake',servername,('0.0.0.0',int(sys.argv[2])),sys.argv[3:])
	g_irc = ircd.serve(('0.0.0.0',int(sys.argv[1])))
	g_irc.start()
	ircd.s2s.start()
	print 'now serving'
	try:
		while True:
			gevent.sleep(60)
	except KeyboardInterrupt:
		ircd.s2s.kill()
		g_irc.kill()
		print
	print 'done'
