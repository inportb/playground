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

import urllib
import random
import os
import sys
import Image, ImageDraw, ImageFont
from ftplib import FTP

class MemeGen(callbacks.Plugin):
    """Add the help for "@plugin help MemeGen" here
    This should describe *how* to use this plugin."""
    threaded = True

    def memegen(self, irc, msg, args, imgurl, writetext):
        """<imgurl> [<writetext>]

        Writes the <writetext> to the image from <imgurl>
        """
	imgurl = str(imgurl)
	writetext = str(writetext)
	ext = imgurl[-4:] #find extension

	# create filename
	filename = random.randrange(1,1001, 2)
	filename = str(filename)

	# open img and write to temp file on system
	tempfile = 'tmp' + ext #where to save
	urllib.urlretrieve(imgurl, tempfile) #Where to get from, where to save
	
	#Process the Meme!
	im = Image.open(tempfile)
	draw = ImageDraw.Draw(im)
	im_size = im.size
	im_h = im.size[1]
	meh = im_h / 7
	im_h = im_h - meh
	im_w = im.size[0]
	
	font = ImageFont.truetype('calibri.ttf', 24) #unix '/usr/share/fonts/truetype/msttcorefonts/arial.ttf'
	
	writetext = str(writetext)
	text_x = 90
	textcolor = "white"
	draw = ImageDraw.Draw(im)
	text_size = draw.textsize(writetext, font=font) # the size of the text box!
	
	# figure out center x placement:
	x = (im_w / 2) - (text_size[0] / 2)
	draw.text((x, im_h ), writetext, font=font, fill=textcolor) 

	im.save(tempfile)
	#connect to ftp
	ftp = FTP('69.175.4.118')
	ftp.set_pasv('true')
	ftp.login('zzbomb','') 
	ftp.cwd('public_html/memegen') # change directory where to store the image, on server
	F=open(tempfile,'r')
	
	#upload by ftp
	ftp.storbinary('STOR ' + filename + ext, file(tempfile, 'rb'))
	ftp.quit()
	F.close()
	os.unlink(tempfile)
	
	irc.reply('http://zzbomb.com/memegen/' + filename + ext)
	
    memegen = wrap(memegen, ['url', 'text'])
Class = MemeGen

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
