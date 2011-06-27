#!/usr/bin/env python
##
## WebQuery: Query the Internet using SQL
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

import urllib, urllib2, json, yaml, apsw
from types import NoneType
from copy import deepcopy
from lxml import etree
from lxml.builder import E
from apsw import SQLITE_INDEX_CONSTRAINT_EQ

USERAGENT = 'Mozilla/5.0 (compatible; WebQuery/0.1; +http://inportb.com/)'

def json2xml(data,**kwargs):
	'''convert a JSON-friendly data structure to an XML-friendly element tree'''
	t = type(data)
	if t == dict:
		return E('dict',*[json2xml(v,key=k) for k,v in data.iteritems()],**kwargs)
	elif t == list:
		return E('list',*[json2xml(i) for i in data],**kwargs)
	else:
		try:
			t = {
				str:		'text',
				unicode:	'text',
				int:		'integer',
				float:		'real',
				NoneType:	'null'
			}[t]
		except KeyError:
			t = 'unknown'
		return E('atom',unicode(data),type=t,**kwargs)

def xml2json(element):
	'''convert an XML-friendly element tree to a JSON-friendly data structure'''
	tag = element.tag
	if '}' in tag:
		tag = tag.rsplit('}',1)[1]
	return tag,dict(map(xml2json,element)) or element.text

class WebQueryModule(object):
	def __init__(self,opener=None):
		if opener is None:
			opener = urllib2.build_opener()
			opener.addheaders = [('user-agent',USERAGENT)]
		self.opener = opener
	def Create(self,connection,modulename,databasename,tablename,*args):
		connection.cursor().execute('CREATE TEMP TABLE IF NOT EXISTS __webquery_v__ (name TEXT UNIQUE, value);');
		return self.Connect(connection,modulename,databasename,tablename,*args)
	def Connect(self,connection,modulename,databasename,tablename,*args):
		table = WebQueryTable(connection,tablename,args[0],opener=self.opener)
		return table.schema,table

class WebQueryTable(object):
	def __init__(self,conn,name,definition,opener):
		self.conn = conn
		self.opener = opener
		if definition.startswith('data:'):
			# load specification from string
			self.spec = spec = yaml.load(definition[5:])
		else:
			try:
				# load specification from local file
				self.spec = spec = yaml.load(open(definition).read())
			except IOError:
				# load specification from remote resource
				self.spec = spec = yaml.load(opener.open(definition).read())
		# get list of fields
		self.fieldlist = fieldlist = tuple(item['field'] for item in spec['binding']['select']['request']['mapping']+spec['binding']['select']['response']['mapping'])
		if len(fieldlist) != len(set(fieldlist)):
			raise KeyError('duplicate field in schema')
		# save number of request fields
		self.requestfieldcount = len(spec['binding']['select']['request']['mapping'])
		# compose schema
		self.Rename(name)
		# get variables
		self.cur = conn.cursor()
		for k,v in spec.get('variable',{}).iteritems():
			self.cur.execute('INSERT INTO __webquery_v__ (name,value) VALUES (?,?)',(name+'_'+k,v))
	def variable_set(self,k,v):
		self.cur.execute('UPDATE __webquery_v__ SET value=? WHERE name=?',(v,self.name+'_'+k))
	def variable_get(self,k):
		for row in self.cur.execute('SELECT value FROM __webquery_v__ WHERE name=?',(self.name+'_'+k,)):
			return row[0]
		raise KeyError(self.name+'_'+k)
	def Rename(self,name):
		try:
			oldname = self.name
		except AttributeError:
			oldname = None
		self.name = name
		spec = self.spec
		self.schema = 'CREATE TABLE %s (%s)'%(name,','.join(tuple('"'+item['field']+'" HIDDEN' for item in spec['binding']['select']['request']['mapping'])+tuple('"'+item['field']+'"' for item in spec['binding']['select']['response']['mapping'])))
		if oldname is not None:
			for k in spec.get('variable',{}):
				self.cur.execute('UPDATE __webquery_v__ SET name=? WHERE name=?',(name+'_'+k,oldname+'_'+k))
	def Open(self):
		return WebQueryCursor(self)
	def BestIndex(self,constraint,orderby):
		requestfieldcount = self.requestfieldcount
		constraintused = []
		constraintnum = []
		constraintoffset = 0
		for num,op in constraint:
			if num < requestfieldcount:
				if op == SQLITE_INDEX_CONSTRAINT_EQ:
					# equality constraint on request field, capture
					constraintused.append(constraintoffset)
					constraintnum.append(chr(num+1))
					constraintoffset += 1
				else:
					# inequality constraint on request field, raise
					raise NotImplementedError('only equality is supported for query parameters')
			else:
				# constraint on response field, ignore
				constraintused.append(None)
		return (constraintused,0,''.join(constraintnum),False,1024)
	def Destroy(self):
		name = self.name
		for k in self.spec.get('variable',{}):
			self.cur.execute('DELETE FROM __webquery_v__ WHERE name=?',(name+'_'+k,))
	Disconnect=Destroy

class WebQueryCursor(object):
	def __init__(self,table):
		self.table = table
		self.opener = table.opener
		self.fieldlist = self.table.fieldlist
		self.requestfieldcount = self.table.requestfieldcount
		self.row = None
		self.rowid = 0
	def iter(self,constraint):
		opener = self.opener
		select = self.table.spec['binding']['select']
		request = select['request']
		response = select['response']
		pagination = select.get('pagination',None)
		# request parameters
		self.requestm = request['mapping']
		self.requestp = requestp = dict((item['field'],item['value']) for item in deepcopy(request['mapping']))
		requestp.update(constraint)
		fmt = response['format']
		# response parameters
		self.responsep = tuple((m['path'],getattr(self,'coerce_'+m['type'].lower())) for m in response['mapping'])
		try:
			# cap requests
			truncate = int(self.table.variable_get('truncate'))
		except KeyError:
			truncate = float('inf')
		try:
			remaining = 1
			requested = 1
			# pagination parameters
			if pagination is not None:
				model = pagination['model']
				if model == 'offset':
					paginationp = {
						pagination['start']['field']:	pagination['start']['value'],
						pagination['size']['field']:	pagination['size']['value']
					}
					requested = pagination['size']['value']
				elif model == 'page':
					paginationp = {
						pagination['page']['field']:	pagination['page']['value'],
						pagination['size']['field']:	pagination['size']['value']
					}
					requested = pagination['size']['value']
				else:
					pagination = None
			total = 0
			while remaining > 0 and total < truncate:
				if pagination is not None:
					requestp.update(paginationp)
				url = request['url']%requestp
				if 'get' in request:
					url += '?'+urllib.urlencode(tuple((item['name'],requestp[item['field']]) for item in request['get']))
				if 'post' in request:
					f = opener.open(url,urllib.urlencode(tuple((item['name'],requestp[item['field']]) for item in request['post'])))
				else:
					f = opener.open(url)
				if fmt == 'json':
					tree = json2xml(json.load(f))
				elif fmt == 'xml':
					tree = etree.parse(f)
				else:
					f.close()
					raise ValueError
				count = 0
				for record in tree.xpath(response['path']):
					count += 1
					yield record
				total += count
				# pagination parameters
				if count >= requested and pagination is not None:
					model = pagination['model']
					if model == 'offset':
						remaining = int(tree.xpath(pagination['total']['path'])[0])-total
						paginationp[pagination['start']['field']] += count
						paginationp[pagination['size']['field']] = requested = min(pagination['size']['value'],remaining)
					elif model == 'page':
						remaining = int(tree.xpath(pagination['total']['path'])[0])-total
						paginationp[pagination['page']['field']] += 1
				else:
					remaining = 0
		finally:
			self.iter = None
	def coerce_null(self,data):
		return None
	def coerce_integer(self,data):
		try:
			return int(data[0])
		except:
			return None
	def coerce_real(self,data):
		try:
			return float(data[0])
		except:
			return None
	def coerce_text(self,data):
		try:
			return unicode(data[0])
		except:
			return None
	def coerce_blob(self,data):
		try:
			return buffer(data[0])
		except:
			return None
	def coerce_json(self,data):
		try:
			return json.dumps(data,separators=(',',':'))
		except:
			return None
	def coerce_etree(self,data):
		try:
			return json.dumps(map(xml2json,data),separators=(',',':'))
		except:
			return None
	def Filter(self,indexnum,indexname,constraintargs):
		fieldlist = self.fieldlist
		self.iter = self.iter(dict(zip(tuple(fieldlist[ord(i)-1] for i in indexname),constraintargs)))
		self.Next()
	def Column(self,num):
		try:
			if num < 0:
				# row id
				return self.rowid
			elif num < self.requestfieldcount:
				# request field
				return self.requestp[self.requestm[num]['field']]
			else:
				# response field
				path,coerce_type = self.responsep[num-self.requestfieldcount]
				return coerce_type(self.row.xpath(path))
		except TypeError:
			pass
	def Rowid(self):
		return self.rowid
	def Next(self):
		try:
			self.row = self.iter.next()
			self.rowid += 1
		except StopIteration:
			pass
	def Eof(self):
		return self.iter is None
	def Close(self):
		pass

if __name__ == '__main__':
	import sys, re
	shell = apsw.Shell()
	mod = WebQueryModule()
	shell.db.createmodule('webquery',mod)
	loaded = []
	for fn in sys.argv[1:]:
		tbl = re.sub(r'\W','_',fn)
		if tbl.endswith('_yml'):
			tbl = tbl[:-4]
		sql = 'CREATE VIRTUAL TABLE %s USING webquery(%s);'%(tbl,fn)
		try:
			shell.process_sql(sql)
			loaded.append('> '+sql+'\r\n')
		except KeyboardInterrupt:
			raise
		except:
			pass
	shell.cmdloop(intro=('SQLite version %s (APSW %s)\r\nEnter ".help" for instructions\r\nEnter SQL statements terminated with a ";"\r\n'%(apsw.sqlitelibversion(),apsw.apswversion()))+''.join(loaded))
