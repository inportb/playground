import BeautifulSoup 
import re

from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
import re
import socket


port = 80

f = open('all.htm', 'r')
data = f.read()
soup = BeautifulSoup(''.join(data), selfClosingTags=['a'])

postarray = soup.findAll( attrs={"class" : "post"}, limit=None, recursive=True)
total = 0
online = 0

for i in range(len(postarray)):
	bodymeh = postarray[i].find(attrs={"class" : "body"})
	##print bodymeh
	if bodymeh != '':
		firsta = bodymeh.find('a')
		if firsta != '':
			stringyay = str(firsta)
			stringtest = stringyay.find('href')
			##print stringtest
			if stringtest > 0:
				output = firsta['href']
				print firsta
				if output != '':
					parsedurl = urlparse(output)
					print parsedurl[1]
					total = total +1
					try:
						s = socket.socket()
						s.settimeout(3)
						s.connect((parsedurl[1], port))
						online = online +1
						print "Percent Online: " + str((online/total)*100) + "%, Total: " + str(total) + ", Online: " + str(online) + "\n" 
						s.close()
					except Exception, e:
						print("fail")
