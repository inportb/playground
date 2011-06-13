import networkx
from gevent import spawn, joinall
from random import getrandbits
from struct import pack
from base64 import urlsafe_b64encode
from jsonrpc import BaseHandler

class ClusterHandler(BaseHandler):
	def __init__(self,protocol):
		BaseHandler.__init__(self,protocol)
		self.node = protocol.node
		self.call = protocol.call
		self.notify = protocol.notify
		self.uid = None
	def startup(self):
		self.notify('netstartup',self.node.uid,self.node.graph.edges())
	def shutdown(self):
		self.node.remove(self)
	def do_netstartup(self,uid,edges):
		self.uid = uid
		self.node.add(self,edges)
	def do_net(self,dst,block,method,params):
		node = self.node
		uid = node.uid
		res = {}
		inc = False
		try:
			if uid in dst:
				inc = True
		except:
			pass
		if dst is None or inc:
			try:
				h = getattr(self,'net_'+method)
				res[uid] = h(*params)
			except GreenletExit:
				return
			except:
				pass
		if dst is None or not inc:
			if block:
				job = node.call(dst,self.uid,method,*params)
			else:
				node.notify(dst,self.uid,method,*params)
				job = None
		if block:
			if job is not None:
				joinall(job)
				for v in job.itervalues():
					res.update(v.get())
			return res
	def net_connect(self,edges):
		return self.node.connect(edges)
	def net_disconnect(self,edges):
		return self.node.disconnect(edges)

class NetworkNode(object):
	def __init__(self,uid=None):
		if uid is None:
			uid = self.randuid()
		self.uid = uid
		self.peer = {}
		self.graph = networkx.Graph()
		self.maketree()
	def add(self,peer,edges):
		self.peer[peer.uid] = peer
		edges.append((self.uid,peer.uid))
		self.notify_all('connect',edges)
		self.connect(edges)
	def connect(self,edges):
		self.graph.add_edges_from(edges)
		self.maketree()
	def remove(self,peer):
		try:
			del self.peer[peer.uid]
		except KeyError:
			pass
		else:
			edges = ((self.uid,peer.uid),)
			self.disconnect(edges)
			self.notify_all('disconnect',edges)
	def disconnect(self,edges):
		self.graph.remove_edges_from(edges)
		self.maketree(prune=True)
	def call(self,dst,exc,method,*params):
		peer = self.peer
		if dst is None:
			return [spawn(peer[via].call,'net',dst,True,method,params) for via in self.via if via != exc]
		else:
			route = self.route
			dst = tuple(k for k in dst if k != exc and k in route)
			return [spawn(peer[route[k]].call,'net',dst,True,method,params) for k in dst]
	def notify(self,dst,exc,method,*params):
		peer = self.peer
		if dst is None:
			for via in self.via:
				if via != exc:
					peer[via].notify('net',dst,False,method,params)
		else:
			route = self.route
			dst = tuple(k for k in dst if k != exc and k in route)
			for k in dst:
				peer[route[k]].notify('net',dst,False,method,params)
	def call_one(self,dst,method,*params):
		return self.call([dst],None,method,*params)
	def notify_one(self,method,*params):
		return self.notify([dst],None,method,*params)
	def call_some(self,dst,method,*params):
		return self.call(dst,None,method,*params)
	def notify_some(self,dst,method,*params):
		return self.notify(dst,None,method,*params)
	def call_all(self,method,*params):
		return self.call(None,None,method,*params)
	def notify_all(self,method,*params):
		return self.notify(None,None,method,*params)
	def maketree(self,prune=False):
		try:
			self.tree = tree = networkx.minimum_spanning_tree(self.graph)
			path = networkx.single_source_dijkstra_path(tree,self.uid)
		except KeyError:
			self.route = self.via = {}
			return
		self.route = route = dict((node,path[1]) for node,path in path.iteritems() if len(path) > 1)
		self.via = via = {}
		for k,v in route.iteritems():
			try:
				via[v].append(k)
			except KeyError:
				via[v] = [k]
		if prune:
			gr = self.graph
			prune = set(gr.nodes())-set(path)
			prune.discard(self.uid)
			gr.remove_nodes_from(prune)
	@staticmethod
	def randuid():
		return urlsafe_b64encode(pack('!Q',getrandbits(64))+pack('!Q',getrandbits(64))).rstrip('=')

__all__ = ['ClusterHandler','NetworkNode']

if __name__ == '__main__':
	from gevent import sleep
	from jsonrpc import JSONPeer
	class Handler(ClusterHandler):
		def net_connect(self,msg):
			print self.uid,msg
			return ClusterHandler.net_connect(self,msg)
		def net_disconnect(self,msg):
			print self.uid,msg
			return ClusterHandler.net_disconnect(self,msg)
		def net_print(self,msg):
			print self.uid,'hi'
	print 'preparing peers...'
	node0 = NetworkNode(uid=8000)
	peer = JSONPeer(('0.0.0.0',8000),handle=ClusterHandler,node=node0)
	peer.start()
	node1 = NetworkNode(uid=8001)
	peer = JSONPeer(('0.0.0.0',8001),handle=ClusterHandler,node=node1)
	peer.start()
	node2 = NetworkNode(uid=8002)
	peer = JSONPeer(('0.0.0.0',8002),handle=ClusterHandler,node=node2)
	peer.start()
	node3 = NetworkNode(uid=8003)
	peer = JSONPeer(('0.0.0.0',8003),handle=ClusterHandler,node=node3)
	peer.start()
	node4 = NetworkNode(uid=8004)
	peer = JSONPeer(('0.0.0.0',8004),handle=ClusterHandler,node=node4)
	peer.start()
	print 'connecting peers...'
	c01 = JSONPeer.connect(('127.0.0.1',8000),handle=ClusterHandler,node=node1)
	c02 = JSONPeer.connect(('127.0.0.1',8000),handle=ClusterHandler,node=node2)
	c12 = JSONPeer.connect(('127.0.0.1',8001),handle=ClusterHandler,node=node2)
	c23 = JSONPeer.connect(('127.0.0.1',8002),handle=ClusterHandler,node=node3)
	c24 = JSONPeer.connect(('127.0.0.1',8002),handle=ClusterHandler,node=node4)
	c34 = JSONPeer.connect(('127.0.0.1',8003),handle=ClusterHandler,node=node4)
	print 'routes:'
	sleep(1)
	print node0.uid,node0.route
	print node1.uid,node1.route
	print node2.uid,node2.route
	print node3.uid,node3.route
	print node4.uid,node4.route
