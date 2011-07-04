#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

import gevent, gevent.wsgi, bottle
from bottle import Bottle, static_file, redirect, request

def Application():
	app = Bottle()
	app.catchall = False
	# tasks
	@app.route('/task',method='POST')
	def post_task():
		return {'result':False}
	@app.route('/task/:uid',method='GET')
	def get_task(uid):
		return {}
	# solutions
	@app.route('/solution',method='POST')
	def post_solution():
		return {'result':False}
	@app.route('/solution/:uid',method='GET')
	def get_solution(uid):
		return {}
	# votes
	@app.route('/vote',method='POST')
	def post_vote():
		return {'result':False}
	# static files
	@app.route('/')
	def http_index():
		return static_file('index.htm',root='./www')
	@app.route('/:path#.+#')
	def http_static(path):
		return static_file(path,root='./www')
	return app

if __name__ == '__main__':
	try:
		gevent.wsgi.WSGIServer(('',8060),Application()).serve_forever()
	except KeyboardInterrupt:
		print
