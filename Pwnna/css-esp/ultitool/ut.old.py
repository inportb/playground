# -----------------------------------------------------------------
# UltiToolModule 0.2 Beta
# For importing purposes
# By Ulti
# http://thekks.net
# Feel free to modify it too your likings. Do not remove this msg.
# Released under Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported
# More info about the license, please see http://creativecommons.org/licenses/by-nc-sa/3.0/
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Requirements:
# EventScripts 2.0 or higher
# =================================================================
# Changelog:
# ---0.1---
# Initial Public Release
# ---0.2---
# Added basic authorization
# Added an echo function
# Added a rename function
# Added a function to convert "item1;item2;item3" to a list ["item1", "item2", "item3"]

##################################################################

import es
import playerlib

def announce(method,userid):
    name = playerlib.getPlayer(userid).name # Get player name
    es.msg("#multi","#green[UltiTool] #defaultThe admin %s %s!" % (method,name)) # Announce

def burn(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid) # Check for problems
    else:
        player = playerlib.getPlayer(userid)
        player.burn()
        if varAnnounce == 1:
            announce("burned",userid)

def extinguish(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.extinguish()
        if varAnnounce == 1:
            announce("extinguished",userid)

def freeze(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.freeze(1)
        if varAnnounce == 1:
            announce("freezed",userid)

def unfreeze(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.freeze(0)
        if varAnnounce == 1:
            announce("unfreezed",userid)

def slay(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        es.sexec(userid, "kill")
        if varAnnounce == 1:
            announce("slayed",userid)

def blind(userid, alpha, duration, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.flash(alpha,duration)
        if varAnnounce == 1:
            announce("blinded",userid)

def noclip(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.noclip = 1
        if varAnnounce == 1:
            announce("nocliped",userid)

def unnoclip(userid, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.noclip = 0
        if varAnnounce == 1:
            announce("unnocliped",userid)

def slap(userid, dmg, varAnnounce=1):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        player = playerlib.getPlayer(userid)
        player.health -= int(dmg)
        if varAnnounce == 1:
            announce("slapped",userid)

def changename(userid, newName):
    if es.exists("userid",userid) == 0:
        echo("[UltiTool] %s is not a valid userid!" % userid)
    else:
        es.cexec(userid,"name %s" % newName)

    
def echo(msg):
    msg = str(msg)
    es.server.queuecmd("echo %s" % msg)

def strListConv(s):
    delimiter = ";"
    newList = s.split(delimiter)
    return newList

#########################################################################
############################# Authorization #############################
#########################################################################
            
def authorize(userid, method, authorized):
    adminList = strListConv(authorized)
    player = playerlib.getPlayer(userid) # get the player
    if method.lower() == "ip": # get the identification method
        colon = player.address.find(":") 
        if colon > -1:
            IP = player.address[:colon] # Kill the port number in the IP
            if IP in adminList:
                return True # Confirm it's player is an admin
            else:
                return False 
    elif method.lower() == "id":
        if player.steamid in adminList:
            return True
        else:
            return False
