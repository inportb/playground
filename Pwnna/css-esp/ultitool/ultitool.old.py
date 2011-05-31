# -----------------------------------------------------------------
# UltiTool 0.2 Beta
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
# Integrated 16k
# Integrated a damage displayer
# Added chat commands.
# Added a rename function
# Optimized codes

##################################################################

import es
import playerlib
import usermsg
import ut
import cmdlib

# Config #
announcing = 1 # 1 will announce. 0 will disable announcing
enableDmgDisplay = 0 # 1 will display damage, 0 will disable damage display
enable16k = 0 # 1 will give you 16k at start of the round, 0 will disable that

identifyMethod = "ip" # "ip" will identify using IP address. "id" will identify using Steam ID.
adminList = "127.0.0.1" # List of admins, seperated by ;
# Config Ends Here #

info = es.AddonInfo()
info.name         = "UltiTool"
info.version      = "0.2 Beta"
info.author       = "Ulti"
info.description  = "Set various player options via Console Command"
info.url          = "http://addons.eventscripts.com/addons/view/ultitool"
info.basename     = "ultitool"


def load():
    # Register a bunch of command
    cmdlib.registerServerCommand("ut_burn", burn, "Burns a player")
    cmdlib.registerServerCommand("ut_extinguish", extinguish, "Extinguishes a player")
    cmdlib.registerServerCommand("ut_freeze", freeze, "Freezes a player")
    cmdlib.registerServerCommand("ut_unfreeze", unfreeze, "Unfreezes a player")
    cmdlib.registerServerCommand("ut_slay", slay, "Slays a player")
    cmdlib.registerServerCommand("ut_blind", blind, "Blinds a player")
    cmdlib.registerServerCommand("ut_noclip", noclip, "Noclips a player without sv_cheats")
    cmdlib.registerServerCommand("ut_unnoclip", unnoclip, "Unnoclips a player.")
    cmdlib.registerServerCommand("ut_slap", slap, "Slaps a player")
    cmdlib.registerServerCommand("ut_name", name, "Renames a player")
    
    # Register Say Commands
    cmdlib.registerSayCommand("!admin", telladmin, "Shows admins that's currently online")
    cmdlib.registerSayCommand("!admins", telladmin, "Shows admins that's currently online")
    cmdlib.registerSayCommand("!burn", sayburn, "Burns a player")
    cmdlib.registerSayCommand("!extinguish", sayextinguish, "Extinguishes a player")
    cmdlib.registerSayCommand("!freeze", sayfreeze, "Freezes a player")
    cmdlib.registerSayCommand("!unfreeze", sayunfreeze, "Unfreezes a player")
    cmdlib.registerSayCommand("!slay", sayslay, "Slays a player")
    cmdlib.registerSayCommand("!blind", sayblind, "Blinds a player")
    cmdlib.registerSayCommand("!noclip", saynoclip, "Noclips a player without sv_cheats")
    cmdlib.registerSayCommand("!unnoclip", sayunnoclip, "Unnoclips a player.")
    cmdlib.registerSayCommand("!slap", sayslap, "Slaps a player")
    cmdlib.registerSayCommand("!name", sayname, "Renames a player")
    
    # Register variable
    if es.exists("variable", "ut_announce") == 0:
        es.ServerVar("ut_announce", announcing)

    if es.exists("variable", "ut_displaydmg") == 0:
        es.ServerVar("ut_displaydmg", enableDmgDisplay)
        es.flags("add", "notify", "ut_displaydmg")

    if es.exists("variable", "ut_16k") == 0:
        es.ServerVar("ut_16k", enable16k)
        es.flags("add", "notify", "ut_16k")

    es.ServerVar("ut_version", info.version).makepublic()

def unload():
    cmdlib.unregisterServerCommand("ut_burn")
    cmdlib.unregisterServerCommand("ut_extinguish")
    cmdlib.unregisterServerCommand("ut_freeze")
    cmdlib.unregisterServerCommand("ut_unfreeze")
    cmdlib.unregisterServerCommand("ut_slay")
    cmdlib.unregisterServerCommand("ut_blind")
    cmdlib.unregisterServerCommand("ut_noclip")
    cmdlib.unregisterServerCommand("ut_unnoclip")
    cmdlib.unregisterServerCommand("ut_slap")
    cmdlib.unregisterServerCommand("ut_name")

    cmdlib.unregisterSayCommand("!burn")
    cmdlib.unregisterSayCommand("!extinguish")
    cmdlib.unregisterSayCommand("!freeze")
    cmdlib.unregisterSayCommand("!unfreeze")
    cmdlib.unregisterSayCommand("!slay")
    cmdlib.unregisterSayCommand("!blind")
    cmdlib.unregisterSayCommand("!noclip")
    cmdlib.unregisterSayCommand("!unnoclip")
    cmdlib.unregisterSayCommand("!slap")
    cmdlib.unregisterSayCommand("!name")

    cmdlib.unregisterSayCommand("!admin")
    cmdlib.unregisterSayCommand("!admins")

### EVENTS ###

def player_hurt(event_var):
    if es.ServerVar("ut_displaydmg") == 1:
        att = event_var["attacker"]
        dmg = int(event_var["dmg_health"])
        usermsg.hudhint(att, "Damages: %s" % (dmg)) # Display Damage

def player_spawn(event_var):    
    if es.ServerVar("ut_16k") == 1:
        if event_var["es_userteam"] > 1:
            es.tell(event_var["userid"], "#multi", "#green[UltiTool] #defaultYou're given 16k every round!")
            playerlib.getPlayer(event_var["userid"]).setCash(16000) # Set Cash

### MAIN FUNCTIONS ###

def telladmin(args):
    nameList = []
    playerList = es.getUseridList()
    for player in playerList:
        if ut.authorize(player,identifyMethod,adminList):
            nameList.append(playerlib.getPlayer(player).name)
    if len(nameList) == 0:
        es.tell(es.getcmduserid(), "#multi", "#green[UltiTool] #defaultThere are no admins online!")
    elif len(nameList) == 1:
        es.tell(es.getcmduserid(), "#multi", "#green[UltiTool] #defaultThe admin that's currently on the server is: " + ", ".join(nameList))
    else:
        es.tell(es.getcmduserid(), "#multi", "#green[UltiTool] #defaultThe admins that's currently on the server are: " + ", ".join(nameList))

def name(args, say=False, cmduserid=0):
    target = args[0]
    newName = args[1]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.changename(target,newName,aVar)
    else:
        ut.changename(target,newName,aVar)

def extinguish(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.extinguish(target,aVar)
    else:
        ut.extinguish(target,aVar)

def freeze(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.freeze(target,aVar)
    else:
        ut.freeze(target,aVar)

def burn(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.burn(target,aVar)
    else:
        ut.burn(target,aVar)

def unfreeze(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.unfreeze(target,aVar)
    else:
        ut.unfreeze(target,aVar)

def slay(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.slay(target,aVar)
    else:
        ut.slay(target,aVar)

def blind(args, say=False, cmduserid=0):
    target = args[0]
    alpha = args[1]
    duration = args[2]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.blind(target,alpha,duration,aVar)
    else:
        ut.blind(target,alpha,duration,aVar)

def noclip(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.noclip(target,aVar)
    else:
        ut.noclip(target,aVar)

def unnoclip(args, say=False, cmduserid=0):
    target = args[0]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.unnoclip(target,aVar)
    else:
        ut.unnoclip(target,aVar)

def slap(args, say=False, cmduserid=0):
    target = args[0]
    dmg = args[1]
    aVar = int(es.ServerVar("ut_announce"))
    if say == True:
        if ut.authorize(cmduserid, identifyMethod, adminList):
            ut.slap(target,dmg,aVar)
    else:
        ut.slap(target,dmg,aVar)



### SAY FUNCTIONS ###

def sayburn(userid, args):
    burn(args, True, userid)

def sayextinguish(userid, args):
    extinguish(args, True, userid)

def sayfreeze(userid, args):
    freeze(args, True, userid)

def sayunfreeze(userid, args):
    unfreeze(args, True, userid)

def sayslay(userid, args):
    slay(args, True, userid)

def sayblind(userid, args):
    blind(args, True, userid)

def saynoclip(userid, args):
    noclip(args, True, userid)

def sayunnoclip(userid, args):
    unnoclip(args, True, userid)

def sayslap(userid, args):
    slap(args, True, userid)

def sayname(userid, args):
    name(args, True, userid)

