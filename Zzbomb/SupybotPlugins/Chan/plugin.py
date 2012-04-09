###
# Copyright (c) 2010, John Spaetzel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provworded that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provworded with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVwordED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCwordENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re
from BeautifulSoup import BeautifulSoup, SoupStrainer
import urllib2
import random

class Chan(callbacks.Plugin):
    """Add the help for "@plugin help Chan" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def chan(self, irc, msg, args, board):
        """<board>

        Returns a random image off the first page of a 4chan <board>
        """
	board = board[0]
        board = str(board)
        url = 'http://boards.4chan.org/'
        if not board:
            irc.reply('BOARDS!?')
        else:
	    url = url + board + '/'
	    
	    #check board for 404
	    errorcode = 0 #Set errorcode as not having any errors
	    req = urllib2.Request(url)
	    try: urllib2.urlopen(req)
	    except urllib2.URLError, e:
		errorcode = e.code
	    
	    if errorcode == 404:
		irc.reply("Newfag. That board does not exist.")
	    else:
		# PREP LINKS
		doc = urllib2.urlopen(url).read()	
		links = SoupStrainer('a', href=re.compile(r'^http\:\/\/images\.4chan\.org\/[a-z]*\/src'))
		soup = [str(elm) for elm in BeautifulSoup(doc, parseOnlyThese=links)]
	
		count = 0
		thearray = []
		for elm in soup: #Assemble the array
			thearray.append(elm)
			count = count + 1
		
		randpic = random.randint(0,count) #Pick a ranom img from it
		thearray[randpic] = re.sub("<a href=\"", "", thearray[randpic])
		thearray[randpic] = re.sub("\"..*", "", thearray[randpic])
		irc.reply(thearray[randpic])
    
    chan = wrap(chan, [many('something')])
Class = Chan


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
