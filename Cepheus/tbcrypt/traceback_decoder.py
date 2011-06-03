#!/usr/bin/env python
# Licensed under a license similar to the FreeBSD license. See COPYING
# included with this file for more information.

from optparse import OptionParser
from Crypto.PublicKey import RSA
import sys
import base64

usage = "usage: %prog [options] traceback"
parser = OptionParser(usage=usage)
parser.add_option("-k", "--key", dest="keyfile", help="Use RSA private key KEY", metavar="KEY")
parser.add_option("-f", "--file", dest="outfile", help="Write traceback to file FILE (default stdout)", metavar="FILE")

(options, args) = parser.parse_args()

if len(args) == 0:
	print "No traceback supplied. Aborting..."
	sys.exit(-1)

if options.keyfile:
	filename = options.keyfile
else:
	filename = "traceback_key.prv"

key = None
	
with open(filename) as f:
	key = f.read()

crypto_obj = RSA.importKey(key)

raw = ""
with open(args[0]) as f:
	for line in f:
		if not line.startswith("-"):
			raw += line
raw = raw.replace("\n", "")
raw = base64.b64decode(raw)

if options.outfile:
	with open(options.outfile, "w") as f:
		f.write(crypto_obj.decrypt(raw))
else:
	print "Decrypted traceback:"
	print crypto_obj.decrypt(raw)
			