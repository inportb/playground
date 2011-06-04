#!/usr/bin/env python
# Licensed under a license similar to the FreeBSD license. See COPYING
# included with this file for more information.
"""tbcrypt

Encrypt tracebacks. Entirely useless but works.
Requires pycrypto.
"""

from Crypto.PublicKey import RSA
from Crypto.Random import random
import sys 
import traceback
import os
import base64

key = None

with open(os.path.join(os.path.dirname(__file__), "traceback_key.pub")) as f:
	key = f.read()
	
_crypto_obj = RSA.importKey(key)

# dreams
# they fade, disappear in the light
# they're lost when you open your eyes
# she's somewhere out there, out of reach and out of sight
def _trace(type, val, tb):
	tb = "".join(traceback.format_exception(type, val, tb))
	tb = _crypto_obj.encrypt(tb, random.getrandbits(512))[0]
	tb = base64.b64encode(tb)
	tb = '\n'.join(tb[i:i+64] for i in xrange(0, len(tb), 64)) # oneliner to linebreak every 64 chars
	print "### Python Application Crash! ###"
	print "The author of this script has protected his tracebacks with TBCrypt."
	print "Please send the following encrypted traceback to the author:"
	print "-----BEGIN ENCRYPTED TRACEBACK-----"
	print tb
	print "-----END ENCRYPTED TRACEBACK-----"
	
	

sys.excepthook = _trace
	
if __name__ == "__main__":
	raise Exception