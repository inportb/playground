# A Comet Session Protocol implementation for gevent, example
# ported to gevent by Jiang Yio <http://inportb.com/>
# based on csp_eventlet_jsio_example by Michael Carter
#     <http://github.com/mcarter/csp_eventlet_jsio_example>
#
# This example uses js.io (included) and Paste.

import os, gevent.pywsgi

from paste import urlmap, urlparser
from csp_gevent import Listener

static_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'example')

class Server(object):
  
	def __init__(self, interface='', port=8000):
		self.wsgi = urlmap.URLMap()
		self.wsgi['/'] = urlparser.StaticURLParser(static_path)
		self.csp_listener = Listener()
		self.wsgi['/csp'] = self.csp_listener
		self.interface = interface
		self.port = port
		
	def run(self):
		gevent.pywsgi.WSGIServer((self.interface, self.port), self.wsgi).start()
		while True:
			sock, addr = self.csp_listener.accept()
			gevent.spawn(self.dispatch, sock, addr)
			
	def dispatch(self, sock, addr):
		sock.send('Welcome!')
		while True:
			try:
				print 'wait for data'
				data = sock.recv(4096)
				print 'Received', data
				if not data:
					# socket is closed
					break
				sock.send(data)
			except Exception, e:
				print 'Exception with csp sock', sock, e
				break
		print 'csp socket is closed'

if __name__ == "__main__":
	s = Server()
	try:
		s.run()
	except KeyboardInterrupt:
		print "Ctr-C pressed, exiting"
