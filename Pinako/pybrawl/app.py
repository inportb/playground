#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

import gevent, gevent.wsgi, bottle
from bottle import Bottle, static_file, redirect, request

def Application():
	app = Bottle()
	app.catchall = False
	@app.route('/')
	def index():
		return static_file('index.htm',root='./www')
	@app.route('/:path#.+#')
	def static(path):
		return static_file(path,root='./www')
	return app

if __name__ == '__main__':
	try:
		gevent.wsgi.WSGIServer(('',8060),Application()).serve_forever()
	except KeyboardInterrupt:
		print
