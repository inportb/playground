from json import loads, dumps
from gevent import Greenlet, GreenletExit, socket, spawn
from gevent.queue import Queue
from gevent.event import AsyncResult
from gevent.server import StreamServer

class RPCError(BaseException):
	def __init__(self,code,message,data=None):
		self.value = {'code':code,'message':message}
		if data is not None:
			self.value['data'] = data
	def __str__(self):
		return dumps(self.value,separators=(',',':'))

class BaseHandler(object):
	def __init__(self,protocol):
		self.protocol = protocol
	def startup(self):
		pass
	def shutdown(self):
		pass

class JSONProtocol(Greenlet):
	def __init__(self,sock,addr,handle,node=None):
		Greenlet.__init__(self)
		self.sock = sock
		self.addr = addr
		self.handle = handle
		self.node = node
		self.queue = Queue()
		self.result = {}
		self.context = 0
	def _run(self):
		sendloop = spawn(self.sendloop)
		sockfile = self.sock.makefile('rb')
		handle = self.handle(self)
		dispatch = self.dispatch
		result = self.result
		spawn(handle.startup)
		try:
			while True:
				line = sockfile.readline()
				if len(line) < 1:
					return
				try:
					msg = loads(line)
				except ValueError:
					self.send({'jsonrpc':'2.0','error':{'code':-32700,'message':'ParseError'},'id':None})
					continue
				version = msg['jsonrpc']
				if version == '2.0':
					if 'method' in msg:
						try:
							params = msg['params']
						except KeyError:
							raise RPCError(-32600,'InvalidRequest')
						else:
							try:
								h = getattr(handle,'do_'+msg['method'])
							except TypeError:
								raise RPCError(-32600,'InvalidRequest')
							except AttributeError:
								raise RPCError(-32601,'Method not found')
						spawn(dispatch,h,params,msg.get('id',None))
					elif 'result' in msg:
						try:
							result.pop(msg['id']).set(msg['result'])
						except KeyError:
							continue
					elif 'error' in msg:
						ex = msg['error']
						try:
							r = result.pop(msg['id'])
						except KeyError:
							continue
						else:
							try:
								r.set_exception(RPCError(ex['code'],ex['message'],ex.get('data',None)))
							except KeyError:
								r.set_exception(RPCError(-32603,'InternalError'))
				else:
					self.send({'jsonrpc':'2.0','error':{'code':-32600,'message':'InvalidRequest'},'id':None})
		except IOError:
			pass
		finally:
			sendloop.kill()
			sockfile.close()
			self.sock.close()
			for r in result.itervalues():
				r.set_exception(IOError)
			handle.shutdown()
	def sendloop(self):
		get = self.queue.get
		sendall = self.sock.sendall
		try:
			while True:
				sendall(get())
		except (TypeError,IOError):
			pass
	def send(self,msg):
		self.queue.put(dumps(msg,separators=(',',':'))+'\r\n')
	def call(self,*args,**kwargs):
		try:
			method = args[0]
		except IndexError:
			raise RPCError(-32600,'InvalidRequest')
		ctx = self.context
		self.send({'jsonrpc':'2.0','method':method,'params':kwargs if len(kwargs) > 0 else args[1:],'id':ctx})
		self.context += 1
		self.result[ctx] = r = AsyncResult()
		return r.get()
	def notify(self,*args,**kwargs):
		try:
			method = args[0]
		except IndexError:
			raise RPCError(-32600,'InvalidRequest')
		self.send({'jsonrpc':'2.0','method':method,'params':kwargs if len(kwargs) > 0 else args[1:]})
	def dispatch(self,h,params,ctx=None):
		ptype = type(params)
		try:
			if ptype is list:
				msg = h(*params)
			elif ptype is dict:
				msg = h(**params)
			else:
				raise RPCError(-32600,'InvalidRequest')
		except GreenletExit:
			pass
		except RPCError,ex:
			if ctx is not None:
				msg = self.send({'jsonrpc':'2.0','error':ex.value,'id':ctx})
		except Exception,ex:
			if ctx is not None:
				msg = self.send({'jsonrpc':'2.0','error':{'code':-32099,'message':str(ex)},'id':ctx})
		else:
			if ctx is not None:
				self.send({'jsonrpc':'2.0','result':msg,'id':ctx})

class JSONPeer(StreamServer):
	def __init__(self,listener,handle=BaseHandler,backlog=None,spawn='default',node=None,**ssl_args):
		StreamServer.__init__(self,listener,handle=None,backlog=backlog,spawn=spawn,**ssl_args)
		self.hnd = handle
		self.node = node
	def handle(self,sock,addr):
		p = JSONProtocol(sock,addr,self.hnd,self.node)
		p.start()
		return p
	@staticmethod
	def connect(listener,handle=BaseHandler,node=None):
		if isinstance(listener,tuple):
			sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sock.connect(listener)
			addr = listener
			listener = sock
		else:
			addr = listener.getpeername()
		p = JSONProtocol(sock,addr,handle,node)
		p.start()
		return p

__all__ = ['RPCError','BaseHandler','JSONProtocol','JSONPeer']

if __name__ == '__main__':
	import time
	from gevent import sleep
	class Handler(BaseHandler):
		def do_time(self):
			return time.time()
		def do_echo(self,data):
			return '[%d] %s'%(self.protocol.call('time'),data)
	peer = JSONPeer(('0.0.0.0',8000),handle=Handler)
	peer.start()
	hnd = peer.connect(('127.0.0.1',8000),handle=Handler)
	print hnd.call('echo','Hello, JSON.')
