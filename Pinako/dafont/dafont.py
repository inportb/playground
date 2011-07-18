#!/usr/bin/env python

import urllib2, re

USERAGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.10 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30'

def scrape(opener=None):
	if opener is None:
		opener = urllib2.build_opener()
		opener.addheaders = [('user-agent',USERAGENT)]
	# regular expression for link to next collection
	re_next = re.compile(r'<a href="([^"]+)"><img src="/img/(?:theme|page)_suivant(?:e)?\.gif"[^>]*></a>')
	# regular expression for link to font page
	re_font = re.compile(r'img\.dafont\.com/dl/\?f=([^"]+)')
	# bootstrap link
	link = 'theme.php?cat=101&fpp=50'
	while True:	# iterate through all collections
		# fetch collection
		content = opener.open('http://www.dafont.com/'+link).read()
		for m in re_font.finditer(content):	# iterate through all fonts in collection
			m = m.group(1)
			# yield download url
			yield m,'http://img.dafont.com/dl/?f='+m
		# look for link to next page
		m = re_next.search(content)
		if m:	# link found, continue
			link = m.group(1)
		else:	# there is no next page, exit
			break

if __name__ == '__main__':
	import sys, os, logging
	# make logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s\t- %(message)s'))
	logger.addHandler(ch)
	# get destination directory
	try:
		destination = sys.argv[1]
	except IndexError:
		destination = 'download'
	destination = os.path.realpath(destination)
	logger.info('destination='+destination)
	# make destination directory
	try:
		os.mkdir(destination)
	except OSError:
		pass
	# make url opener
	opener = urllib2.build_opener()
	opener.addheaders = [('user-agent',USERAGENT)]
	# keep count
	count = 0
	for name,url in scrape(opener):
		path = os.path.join(destination,name+'.zip')
		try:
			with open(path,'w+') as f:
				f.write(opener.open(url).read())
		except KeyboardInterrupt:
			logger.info('terminated')
			break
		except:
			logger.exception('cannot fetch '+name)
		else:
			logger.info('fetched '+path)
			count += 1
	logger.info('fetched %d files'%count)
