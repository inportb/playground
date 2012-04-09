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
from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener

class UrbanDict(callbacks.Plugin):
    """Add the help for "@plugin help UrbanDict" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def urban(self, irc, msg, args, epicword):
        """<word>

        Returns a definition from urban dictionary.
        <word> specifies which word to retrieve.
        """
	epicword = epicword[0]
        epicword = str(epicword)
        url = 'http://www.urbandictionary.com/define.php?term='
	inportb = 'inportb is a magical place created by the infamous pinako. Its origins are largely unknown as it was created in the beginning of time or possibly earlier. Located on freenode it is often filled with hot lesbians, pedophiles, whores, hoes, gay guys, and guys in denial of being gay. Additionally the channel is frequented by geeks, hackers, and various other forms of the household computer nerd.'
        if not epicword:
            irc.reply('Please specify a word to lookup')
        else:
	    url += epicword
	    ua = 'ZzBot'
	    opener = build_opener()
	    opener.addheaders = [('User-Agent', ua)]
	    html = opener.open(url)
	    html_str = html.read()
	    soup = BeautifulSoup(html_str, convertEntities=BeautifulSoup.HTML_ENTITIES)
	    theword = soup.find("div", { "class" : "definition" })
	    if theword == None:
		if epicword == 'inportb':
		    theword = str(inportb)
		else:
		    theword = str(theword)
		    theword = epicword + ' has no definition.'
	    else:
		theword = str(theword)
		theword = theword.replace('<div class="definition">', '')
		theword = theword.replace('</div>', '' )
        irc.reply(theword)
    
    urban = wrap(urban, [many('something')])
Class = UrbanDict


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
