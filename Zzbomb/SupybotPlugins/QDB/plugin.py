###
# Copyright (c) 2010, John Spaetzel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
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

class QDB(callbacks.Plugin):
    """Add the help for "@plugin help QDB" here
    This should describe *how* to use this plugin."""
    threaded = True

	

    def bash(self, irc, msg, args, id):
        """[<id>]

        Returns a random geek quote from bash.org; the optional argument
        <id> specifies which quote to retrieve.
        """
        url = 'http://bash.org/?'
        if not id:
            id = 'random'
        url += str(id)
        ua = 'ZzBot'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str, convertEntities=BeautifulSoup.HTML_ENTITIES)
        thequote = soup.find("p", { "class" : "qt" })
        if thequote == None:
			thequote = 'Quote #' + str(id) + ' does not exist.'
        else:
        	thequote = str(thequote)
        	thequote = thequote.replace('<p class="qt">', '' )
        	thequote = thequote.replace('</p>', '' )
        	thequote = thequote.replace('<br />\r\n', '  \\\  ' )

        irc.reply(str(thequote))
           
    bash = wrap(bash, [additional(('id', 'bash'))])
    
    def qdb(self, irc, msg, args, id):
        """[<id>]

        Returns a random quote from bash.org; the optional argument
        <id> specifies which quote to retrieve.
        """
        url = 'http://qdb.us/'
        if not id:
            id = 'random'
        url += str(id)
        ua = 'ZzBot'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str, convertEntities=BeautifulSoup.HTML_ENTITIES)
        thequote = soup.find("span", { "class" : "qt" })
        if thequote == None:
			thequote = 'Quote #' + str(id) + ' does not exist.'
        else:
        	thequote = str(thequote)
        	thequote = re.sub("<span class=\"qt\" id=\".*\">", "", thequote)
        	thequote = thequote.replace('</span>', '' )
        	thequote = thequote.replace('<br />\n', '  \\\  ' )

        irc.reply(str(thequote))
           
    qdb = wrap(qdb, [additional(('id', 'qdb'))])

Class = QDB


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
