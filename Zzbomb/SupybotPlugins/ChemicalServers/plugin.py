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


class ChemicalServers(callbacks.Privmsg):
    def __init__(self, irc):
        self.__parent = super(ChemicalServers, self)
        self.__parent.__init__(irc)
        self.whos = {}
        
    def gethelp(self, irc, msg, args):
        """
		Get automated help from our bot: !nameservers, !cpanel, !contact, !forums
        """
        irc.reply('Get automated help from our bot: !nameservers, !cpanel, !contact, !forums')
    gethelp = wrap(gethelp)    
        
    def nameservers(self, irc, msg, args):
        """
		Our Nameservers are NS1.CHEMICALSERVERS.COM and NS2.CHEMICALSERVERS.COM
        """
        irc.reply('Our Nameservers are NS1.CHEMICALSERVERS.COM and NS2.CHEMICALSERVERS.COM')
    nameservers = wrap(nameservers)
    
    def cpanel(self, irc, msg, args):
        """
		Visit our cPanel at http://chemicalservers.com/cpanel/
        """
        irc.reply('Visit our cPanel at http://chemicalservers.com/cpanel/')
    cpanel = wrap(cpanel)
    
    def contact(self, irc, msg, args):
        """
		Email: admin@chemicalservers.com
		Forums: http://chemicalservers.com/forum/
        Support: http://clients.chemicalservers.com/
        """
        irc.reply('Email: admin@chemicalservers.com')
        irc.reply('Forums: http://chemicalservers.com/forum/')
        irc.reply('Support: http://clients.chemicalservers.com/')
    contact = wrap(contact)
    
    def forums(self, irc, msg, args):
        """
		Go check out our forums: http://chemicalservers.com/forum/
        """
        irc.reply('Go check out our forums: http://chemicalservers.com/forum/')
    forums = wrap(forums)
    
    def dedicated(self, irc, msg, args):
        """
		http://chemicalservers.com/?page=dedi
        """
        irc.reply('http://chemicalservers.com/?page=dedi')
    dedicated = wrap(dedicated)

    def vps(self, irc, msg, args):
        """
		http://chemicalservers.com/?page=vps
        """
        irc.reply('http://chemicalservers.com/?page=vps')
    vps = wrap(vps)

    def managed(self, irc, msg, args):
        """
		http://chemicalservers.com/?page=managed
        """
        irc.reply('http://chemicalservers.com/?page=vps')
    managed = wrap(managed)

    def link(self, irc, msg, args):
        """
		http://chemicalservers.com/?page=vps
        """
        irc.reply('http://chemicalservers.com/')
    link = wrap(link)
   
    pass


Class = ChemicalServers


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
