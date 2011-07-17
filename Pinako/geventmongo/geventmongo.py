# based on <http://pastebin.com/V74Bn9NG>

import pymongo
from gevent.queue import Queue

POOL_SIZE = 5

class SocketWrapper(object):
	__slots__ = ('__pool','__sock')
	def __init__(self,pool,sock):
		self.__pool = pool
		self.__sock = sock
	def __getattr__(self,name):
		return getattr(self.__sock,name)
	def __del__(self):
		self.__pool.sockets.put(self.__sock)
		del self.__pool
		del self.__sock

class Pool(object):
	def __init__(self,socket_factory,max_pool_size=POOL_SIZE):
		self.socket_factory = socket_factory
		self.max_pool_size = min(max_pool_size,POOL_SIZE)
		self.sockets = None
	def socket(self):
		if not self.sockets:
			self.initialize()
		return SocketWrapper(self,self.sockets.get())
	def initialize(self):
		self.sockets = Queue(self.max_pool_size)
		for i in range(self.max_pool_size):
			sock = self.socket_factory()
			self.sockets.put(sock)
	def return_socket(self):
		pass

pymongo.connection._Pool = Pool
