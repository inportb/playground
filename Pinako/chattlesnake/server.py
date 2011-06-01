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

import logging, re, gevent
from itertools import izip
from gevent import GreenletExit, socket, sleep
from gevent.server import StreamServer
from gevent.queue import Queue

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s\t- %(message)s'))
logger.addHandler(ch)

RPL_WELCOME		= 001
RPL_NAMREPLY	= 353
RPL_ENDOFNAMES	= 366

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

class IRCChannel(object):
	def __init__(self,server,name):
		self.server = server
		self.name = name
		self.topictext = None
		self.topicsetter = None
		self.client = set()
		self.namreply = ''
	def send(self,src,msg,exclude=None):
		for c in self.client:
			if c is not exclude:
				c.send(src,msg)
	def join(self,client):
		name = self.name
		if client not in self.client:
			self.client.add(client)
			if name[0] == '#' and len(self.client) == 1:
				client.channel[self] = set('o')
			else:
				client.channel[self] = set()
			if self.topictext is not None:
				client.send(self.topicsetter,'TOPIC %s :%s'%(name,self.topictext))
			msg = 'JOIN :'+name
			for c in self.client:
				c.send(client.prefix,msg)
			self.setnamreply()
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
			self.setnamreply()
			return True
		return False
	def setnamreply(self):
		serverclientname = self.server.clientname
		namreply = []
		for client in self.client:
			chanmode = client.channel[self]
			if 'a' in chanmode:
				namreply.append('&'+serverclientname[client])
			elif 'o' in chanmode:
				namreply.append('@'+serverclientname[client])
			elif 'h' in chanmode:
				namreply.append('%'+serverclientname[client])
			elif 'v' in chanmode:
				namreply.append('+'+serverclientname[client])
			else:
				namreply.append(serverclientname[client])
		self.namreply = ' '.join(namreply)

class IRCClient(object):
	re_nick = re.compile(r'[^0-9A-Za-z-_\[\]`^{}]')
	re_chan = re.compile(r'^(?:#|\+)([0-9A-Za-z-_#])+$')
	def __init__(self,server,sock,addr):
		self.server = server
		self.sock = sock
		self.hostname = addr[0]
		self.realname = None
		self.username = None
		self.prefix = None
		self.channel = {}
		self.sendq = Queue()
		self.quit = None
	def run(self):
		logger.info('+client '+self.hostname)
		server = self.server
		send = self.send
		sendloop = gevent.spawn(self.sendloop)
		sockfile = self.sock.makefile('rb')
		try:
			while True:
				line = sockfile.readline().rstrip('\r\n')
				if len(line) < 1:
					break
				try:
					arg,txt = line.split(':',1)
				except ValueError:
					arg = line.split()
				else:
					arg = arg.split()
					arg.append(txt)
				try:
					cmd = arg[0].lower()
					if self.prefix is None and cmd not in ('nick','user','pass','ping'):
						ex = IRCError.NotRegistered
						send(server.prefix,'%03d %s'%(ex.code,ex.message))
						continue
					hnd = getattr(self,'do_'+cmd)
				except IndexError:
					logger.info('invalid command: %s'%line)
				except AttributeError:
					logger.info('no handler for command: %s'%line)
				else:
					try:
						res = hnd(*arg[1:])
					except IRCError,ex:
						send(server.prefix,'%03d :%s'%(ex.code,ex.message))
					except TypeError:
						ex = IRCError.NeedMoreParams
						send(server.prefix,'%03d :%s'%(ex.code,ex.message))
					except GreenletExit:
						break
					except:
						logger.exception('an error occurred')
					else:
						if res is not None:
							send(server.prefix,res)
		finally:
			sendloop.kill()
			sockfile.close()
			self.sock.close()
			msg = 'QUIT' if self.quit is None else ('QUIT :'+self.quit)
			target = set(sum((tuple(channel.client) for channel in self.channel),()))
			target.discard(self)
			for c in target:
				c.send(self.prefix,msg)
			for c in self.channel:
				c.part(self.prefix,None)
			logger.info('-client '+self.hostname)
	def send(self,src,msg):
		self.sendq.put((src,msg))
	def sendloop(self):
		sendall = self.sock.sendall
		get = self.sendq.get
		try:
			while True:
				src,msg = get()
				sendall(':%s %s\r\n'%(src,msg))
		except GreenletExit:
			pass
		finally:
			self.sock.close()
	def setprefix(self,nick=None):
		if nick is None:
			try:
				nick = self.server.clientname[self]
			except KeyError:
				pass
		if nick is not None and self.username is not None:
			self.prefix = '%s!%s@%s'%(nick,self.username,self.hostname)
		else:
			self.prefix = None
	def privmsg(self,target,msg,cmd='PRIVMSG'):
		if target[0] in '#+':
			try:
				c = self.server.channel[target]
				if self not in c.client:
					raise IRCError.CannotSendToChan
			except AttributeError:
				raise IRCError.NoSuchNick
		else:
			try:
				c = self.server.client[target]
			except AttributeError:
				raise IRCError.NoSuchNick
		c.send(self.prefix,'%s %s %s'%(cmd,target,msg),exclude=self)
	def do_nick(self,nick,*args):
		server = self.server
		if nick in server.client:
			if server.client[nick] is self:
				return
			raise IRCError.NicknameInUse
		if len(nick) > 16 or self.re_nick.search(nick):
			raise IRCError.ErroneousNickname
		res = None
		try:
			oldnick = server.clientname[self]
		except KeyError:
			self.send(server.prefix,'%03d %s :%s'%(RPL_WELCOME,nick,server.welcome))
			res = 'NICK :'+nick
		else:
			del server.client[oldnick]
			if self.prefix is None:
				pass
			else:
				_res = 'NICK :'+nick
				for c in set(sum((tuple(channel.client) for channel in self.channel),())):
					c.send(self.prefix,_res)
		server.client[nick] = self
		server.clientname[self] = nick
		self.setprefix(nick)
		return res
	def do_user(self,username,usermode,ign,realname,*args):
		if self.prefix is None:
			self.username = username
			self.usermode = usermode
			self.realname = realname
			self.setprefix()
		else:
			raise IRCError.AlreadyRegistered
	def do_pass(self,password,*args):
		pass
	def do_ping(self,*args):
		if len(args) > 0:
			return 'PONG :%s'%args[0]
		else:
			return 'PONG :%s'%self.server.prefix
	def do_join(self,channel,password=None,*args):
		if password is None:
			channel = dict((cn,'') for cn in channel.split(','))
		else:
			channel = dict((cn,pw) for cn,pw in izip(channel.split(','),password.split(',')))
		server = self.server
		match = self.re_chan.match
		namreply = []
		for cn,pw in channel.iteritems():
			try:
				c = server.channel[cn]
			except KeyError:
				if len(cn) > 32 or not match(cn):
					#raise IRCError.NoSuchChannel
					continue
				c = IRCChannel(server,cn)
				server.channel[cn] = c
				server.channelname[c] = cn
			if c.join(self):
				namreply.append(cn)
		self.do_names(','.join(namreply))
	def do_names(self,channel=None,server=None,*args):
		server = self.server
		send = self.send
		nick = server.clientname[self]
		if channel is None:
			channellist = self.channel.iteritems()
		else:
			channellist = ((cn,server.channel[cn]) for cn in channel.split(','))
		for cn,c in channellist:
			if self in c.client:
				send(server.prefix,'%03d %s = %s %s'%(RPL_NAMREPLY,nick,cn,c.namreply))
		send(server.prefix,'')
		send(server.prefix,'%03d %s %s :End of /NAMES list' % (RPL_ENDOFNAMES,nick,channel))
	def do_privmsg(self,target,msg,*args):
		return self.privmsg(target,msg,'PRIVMSG')
	def do_notice(self,target,msg,*args):
		return self.privmsg(target,msg,'NOTICE')
	def do_part(self,channel,*args):
		args = ' '.join(args)
		server = self.server
		for cn in channel.split(','):
			try:
				c = server.channel[cn]
			except KeyError:
				#raise IRCError.NoSuchChannel
				continue
			c.part(self,args)
	def do_quit(self,*args):
		self.quit = ' '.join(args)
		self.sock.close()

class IRCServer(object):
	def __init__(self,servername):
		self.prefix = self.servername = servername
		self.welcome = 'Welcome to %s!'%servername
		self.channel = {}
		self.channelname = {}
		self.client = {}
		self.clientname = {}
	def serve(self,listener,backlog=None,spawn='default'):
		return StreamServer(listener,handle=self.handle,backlog=backlog,spawn=spawn)
	def handle(self,sock,addr):
		IRCClient(self,sock,addr).run()

if __name__ == '__main__':
	ircd = IRCServer('chattlesnake.localhost')
	ircd.serve(('0.0.0.0',6667)).serve_forever()
