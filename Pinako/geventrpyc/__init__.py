## RPyC-gevent compatibility and monkey-patching code
##
## Copyright (C) 2011 by Jiang Yio <http://inportb.com/>
##
## Includes MIT-licensed code from RPyC:
##   Copyright (c) 2005-2011
##     Tomer Filiba (tomerfiliba@gmail.com)
##     Copyrights of patches are held by their respective submitters
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

from gevent import socket, spawn
try:
	from gevent import ssl
except ImportError:
	pass

from rpyc.core import VoidService
from rpyc.core.stream import SocketStream as BaseSocketStream
from rpyc.utils.server import Server
from rpyc.utils.factory import connect_stream, _get_free_port

class SocketStream(BaseSocketStream):
	@classmethod
	def _connect(cls,host,port,family=socket.AF_INET,socktype=socket.SOCK_STREAM,proto=0,timeout=3,nodelay=False):
		s = socket.socket(family,socktype,proto)
		s.settimeout(timeout)
		s.connect((host,port))
		if nodelay:
			s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
		return s
	@classmethod
	def ssl_connect(cls,host,port,ssl_kwargs,**kwargs):
		if kwargs.pop('ipv6',False):
			kwargs['family'] = socket.AF_INET6
		s = cls._connect(host,port,**kwargs)
		s2 = ssl.wrap_socket(s,**ssl_kwargs)
		return cls(s2)

class TunneledSocketStream(SocketStream):
	__slots__ = ('tun',)
	def __init__(self,sock):
		self.sock = sock
		self.tun = None
	def close(self):
		SocketStream.close(self)
		if self.tun:
			self.tun.close()

class GeventServer(Server):
	def _accept_method(self,sock):
		t = spawn(self._authenticate_and_serve_client,sock)

def connect(host,port,service=VoidService,config={},ipv6=False):
	return connect_stream(SocketStream.connect(host,port,ipv6=ipv6),service,config)
def tlslite_connect(host,port,username,password,service=VoidService,config={},ipv6=False):
	return connect_stream(SocketStream.tlslite_connect(host,port,username,password,ipv6=ipv6),service,config)
def ssl_connect(host,port,keyfile=None,certfile=None,ca_certs=None,ssl_version=None,service=VoidService,config={},ipv6=False):
	ssl_kwargs = {'server_side':False}
	if keyfile:
		ssl_kwargs['keyfile'] = keyfile
	if certfile:
		ssl_kwargs['certfile'] = certfile
	if ca_certs:
		ssl_kwargs['ca_certs'] = ca_certs
	if ssl_version:
		ssl_kwargs['ssl_version'] = ssl_version
	else:
		ssl_kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1
	s = SocketStream.ssl_connect(host,port,ssl_kwargs,ipv6 = ipv6)
	return connect_stream(s,service,config)
def ssh_connect(sshctx,remote_port,service=VoidService,config={}):
	loc_port = _get_free_port()
	tun = sshctx.tunnel(loc_port,remote_port)
	stream = TunneledSocketStream.connect('localhost',loc_port)
	stream.tun = tun
	return Connection(service,Channel(stream),config=config)

def patch_stream():
	_stream = __import__('rpyc.core.stream')
	_stream.SocketStream = SocketStream
	_stream.TunneledSocketStream = TunneledSocketStream
def patch_factory():
	_factory = __import__('rpyc.utils.factory')
	_factory.connect = connect
	_factory.tlslite_connect = tlslite_connect
	_factory.ssl_connect = ssl_connect
	_factory.ssh_connect = ssh_connect
def patch_server():
	_server = __import__('rpyc.utils.server')
	_server.ThreadedServer = GeventServer
def patch_all(stream=True,factory=True,server=True):
	if stream:
		patch_stream()
	if factory:
		patch_factory()
	if server:
		patch_server()

__all__ = ['SocketStream','TunneledSocketStream','GeventServer','connect','tlslite_connect','ssl_connect','ssh_connect','patch_stream','patch_factory','patch_server','patch_all']
