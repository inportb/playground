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


class Zzplugin(callbacks.Privmsg):
    def __init__(self, irc):
        self.__parent = super(Zzplugin, self)
        self.__parent.__init__(irc)
        self.whos = {}
        
    """Zzplugin is Sacred.. Shoo."""
    
    threaded = True
	
    def ayen(self, irc, msg, args):
        irc.reply('Ayen: one who is gifted with adeptness in mathematics, she is focused and precise. ayen is a trustworthy friend, an understanding daughter, a cheerful classmate and a diligent student. she can be depended on because she can defend her friends when called for', prefixNick=False)
    
    def zzbomb(self, irc, msg, args):
        irc.reply('Zzbomb == God.. But wait my name is God!', prefixNick=False)
        
    def mghq(self, irc, msg, args):
        irc.reply('Mghq: Sexiest person ever.', prefixNick=False)
        
    def gabriela(self, irc, msg, args):
        irc.reply('Gabriela: Clearly the hottest chick on all of freenode. We all love her!', prefixNick=False)
        
    def pie(self, irc, msg, args):
        irc.reply('PI = 3.1415926535 8979323846 2643383279 5028841971 6939937510 5820974944 5923078164 0628620899 8628034825 3421170679 8214808651 3282306647 0938446095 5058223172 5359408128 4811174502 8410270193 8521105559 6446229489 5493038196 4428810975 6659334461 2847564823 3786783165 2712019091 4564856692 3460348610', prefixNick=False)
        
    def ladies(self, irc, msg, args):
        irc.reply('Ladies: Shaded extends his love', prefixNick=False)
        
    def shaded(self, irc, msg, args):
        irc.reply('Shaded: That Straight Bastard.', prefixNick=False)

    def pinako(self, irc, msg, args):
        irc.reply('Pinako: Quite possibly is a computer himself... Or some sort of mad scientist.', prefixNick=False)
    
    def adryn(self, irc, msg, args):
        irc.reply('Adryn: Hott? Signs point to yes.', prefixNick=False)
    
    def cepheus(self, irc, msg, args):
        irc.reply('Cepheus: Not Meh at all i sorta promise.', prefixNick=False)
    
    def dazappa(self, irc, msg, args):
        irc.reply('Dazappa: Don\'t ban me!', prefixNick=False)
    
    def epiccyndaquil(self, irc, msg, args):
        irc.reply('EpicCyndaqui: A Fire Pokemon. FAR moar epic than a normal Cyndaquil.', prefixNick=False)
    
    def inportb(self, irc, msg, args):
        irc.reply('#InportB: The BEST IRC channel on teh net.', prefixNick=False)

    def rostislava(self, irc, msg, args):
        irc.reply('Rostislava: Are you going to kill your mate for protein like a praying mantis?', prefixNick=False)

    def cheeseballs(self, irc, msg, args):
        irc.reply('/me eats cheeseballs. Nomnomnom.', prefixNick=False)
        
Class = Zzplugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
