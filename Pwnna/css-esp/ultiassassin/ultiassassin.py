# Constants #
# Change these to change the default settings
VIPHealth = 200                 # Health of the VIP
GuardHealth = 100               # Health of the Guard
AssassinHealth = 500            # Health of the Assassin.
GuardWeapons = ("famas",)       # The avaliable guns to the Guard. Note: DO NOT ADD MORE TO THIS LIST! THERE'S A BUG!
AssassinWeapons = ("awp",
                   "ak47",
                   "aug",
                   "p90",
                   "m4a1")      # The available guns to the Assassin
AssassinAlpha = 40              # The opacity of the Assassin. 0 being completely transparent, 255 is opaque.
AssassinTeam = 2                # The team for the Assassin. 3 is CT, 2 is T
VIPTeam = 3                     # The team for the VIP and the guard.
# Constants #

# Weapon invisibility is accomplished via satoon's post at 
# http://forums.eventscripts.com/viewtopic.php?f=27&t=40276

# +-----------------------------------------------+
# | UltiAssassin v1.1                             |
# | filename: ultiassassin.py                     |
# | Created by Ulti - http://thekks.net           |
# | Status: Release                               |
# | Website: http://thekks.net                    |
# | Requirement: EventScript 2.1 or higher        |
# |              SourcePythonExtension (SPE)      |
# |              UltiLib (Included)               |
# +-----------------------------------------------+
# |                    Credits                    |
# | Design: KKSNetwork                            |
# | Coding: Ultimatebuster                        |
# | Beta Testers: Gonzo                           |
# +-----------------------------------------------+


import es, weaponlib, playerlib, msglib, popuplib

import sys
import random

import gamethread

import psyco
psyco.full()

import ultilib

info = es.AddonInfo()
info.name         = "UltiAssassin"
info.version      = "1.1"
info.author       = "Ulti"
info.description  = "An cool assassin mod"
info.url          = "http://addons.eventscripts.com/addons/view/ultiassassin"
info.basename     = "ultiassassin"

VIPHealth = float(VIPHealth)
GuardHealth = float(GuardHealth)
AssassinHealth = float(AssassinHealth)
started = False
changed = False
  

class Guard(ultilib.EasyPlayer):
    """ The object for a guard. """
    def prepare(self, match):
        """ prepares the player for a match """
        self.switchTeam(int(es.ServerVar("uam_vipteam")))
        self.removePrimary()
        self.replaceSecondaryWeapon("weapon_deagle")
        ultilib.WeaponSelectionMenu(self.userid, GuardWeapons)
        self.resetColor()
        es.give(self.userid, "item_assaultsuit")
        self.health = es.ServerVar("uam_guardhealth")
        self.nightvision = 1
        self.giveSmoke(1)
        self.giveFlash(2)
        self.giveHE(1)
        es.centertell(self.userid, "You're a guard! Protect %s! Kill %s!" % (match.vip.name, match.assassin.name))

class VIP(ultilib.EasyPlayer):
    def prepare(self, match):
        """ prepares the player for a match """
        self.switchTeam(int(es.ServerVar("uam_vipteam")))
        self.removePrimary()
        self.setColor(0, 255, 255, 255)
        self.replaceSecondaryWeapon("weapon_deagle")
        es.give(self.userid, "item_assaultsuit")
        self.armor = 150
        self.health = es.ServerVar("uam_viphealth")
        self.nightvision = 1
        self.giveSmoke(1)
        self.giveFlash(0)
        self.giveHE(0)
        self.setSpeed(1.2)
        es.centertell(self.userid, "You're the VIP. Survive at all cost. The assassin is %s." % match.assassin.name)
        es.dbgmsg(0, "The VIP id is %s" % self.userid)
        
class Assassin(ultilib.EasyPlayer):
    def prepare(self, match):
        """ prepares the player for a match """
        self.switchTeam(int(es.ServerVar("uam_assassinteam")))
        self.removePrimary()
        self.setColor(0, 0, 0, AssassinAlpha)
        self.replaceSecondaryWeapon("weapon_deagle")
        es.give(self.userid, "item_assaultsuit")
        self.armor = 150
        self.health = es.ServerVar("uam_assassinhealth")
        self.nightvision = 1
        self.giveSmoke(2)
        self.giveFlash(3)
        self.giveHE(2)
        self.setSpeed(0.8)
        ultilib.WeaponSelectionMenu(self.userid, AssassinWeapons)
        es.centertell(self.userid, "You're the Assassin. Kill %s!" % match.vip.name)
        es.dbgmsg(0, "The Assassin id is %s" % self.userid)
        

class AssassinModMatch(object):
    """A match. Intialized at round_start """
    def __init__(self, assassinID=None, vipID=None):
        self.manualAssassinID = assassinID
        self.manualVipID = vipID
        self.started = False
        
    def start(self):
        global started, changed
        self.useridList = es.getUseridList()
        
        for userid in self.useridList:
            player = playerlib.getPlayer(userid)
            if player.team < 2 or player.isdead:
                self.useridList.remove(userid)        
        
        if len(self.useridList) < 3:
            es.centermsg("You have to have more than 3 players to play the Assassin mod!")
            return None
        
        if self.useridList:
            ultilib.removeMapObjective()
            
            if self.manualAssassinID:
                self.assassinID = self.manualAssassinID
                self.useridList.remove(self.assassinID)
            else:
                self.assassinID = self._selectOneUserid()
                
            if self.manualVipID:
                self.vipID = self.manualVipID
                self.useridList.remove(self.vipID)
            else:
                self.vipID = self._selectOneUserid()        
            
            self.vip = VIP(self.vipID)
            self.assassin = Assassin(self.assassinID)

            self.guards = {}
            for userid in self.useridList:
                self.guards[userid] = Guard(userid)

            self.vip.prepare(self)
            self.assassin.prepare(self)
            for userid in self.guards.keys():
                self.guards[userid].prepare(self)

            self.aInvisibilityInfo = {"userid": None, "weapon": None, "color": None}
            
            if not changed:

                es.set("mp_limitteams", 20)
                es.set("mp_friendlyfire", 1)
                es.set("mp_autoteambalance", 0)
                es.set("sv_alltalk", 1)
                changed = True
            started = True
            roundtime = int(float(es.ServerVar("mp_roundtime")) * 60.0)
            roundtime += int(float(es.ServerVar("mp_freezetime")) * 60.0)
            gamethread.cancelDelayed("vipwins")
            gamethread.delayedname(roundtime,"vipwins", self.vipWins)
            es.msg("#multi", "#green[UltiAssassin 1.1]#defaultYou're playing the UltiAssassin!")
            
        self.started = True
       
    def _selectOneUserid(self):
        """randomly selects a living, playing player"""
        choice = False
        while not choice:
            choice = self.useridList.pop(random.randint(0, len(self.useridList)-1))
            choiceplayer = playerlib.getPlayer(choice)
            if choiceplayer.team < 2 or choiceplayer.isdead:
                self.useridList.append(choice)
                choice = False
        return choice

    def assassinWins(self):
        """Executes when the assassin wins"""
        global started
        for userid in self.guards.keys():
            self.guards[userid].suicide()
            es.centertell(userid, "You have failed your mission!")
        started = False

    def vipWins(self):
        """Executes when the vip team wins"""
        global started
        self.assassin.suicide()
        es.centermsg("The VIP survives!")
        started = False
    
    def clearAssassinInvisibilityInfo(self):
        self.aInvisibilityInfo.clear()
        
    def tickListener(self):
        if self.started:
            self.assassin.refreshAttributes()
            color = self.assassin.getColor()
            if self.aInvisibilityInfo["userid"] != self.assassinID or self.aInvisibilityInfo["weapon"] != self.assassin.weapon or self.aInvisibilityInfo["color"]:
                self.aInvisibilityInfo["userid"] = self.assassinID
                self.aInvisibilityInfo["color"] = color
                self.aInvisibilityInfo["weapon"] = self.assassin.weapon
                
                self.assassin.setWeaponColor(*color) # Player has no active weapon

theMatch = AssassinModMatch()


def round_start(ev):
    global theMatch, started
    if started:
        started = False
               
    theMatch = AssassinModMatch()
    theMatch.start()

def ticklistener():
    theMatch.tickListener()

def load():
    """ Creates server variables when the script is loaded """
    ultilib.createServerVar("uam_viphealth", VIPHealth, True, "VIP Health")
    ultilib.createServerVar("uam_guardhealth", GuardHealth, True, "Guard Health")
    ultilib.createServerVar("uam_assassinhealth", AssassinHealth, True, "Assassin Health")
    ultilib.createServerVar("uam_assassinteam", AssassinTeam, True, "Assassin Team")
    ultilib.createServerVar("uam_vipteam", VIPTeam, True, "VIP Team")
    es.ServerVar("ultiassassin_version", info.version, "UltiAssassin Version").makepublic()
    es.addons.registerTickListener(ticklistener)
    
def unload():
    es.addons.unregisterTickListener(ticklistener)

def round_end(ev):
    global started
    started = False

def game_end(ev):
    round_end(ev)

def player_spawn(ev):
    if started:
        es.sexec(ev["userid"], "kill")
        es.centertell(ev["userid"], "You may join the game next round!")

def player_hurt(ev):
    if started:
        userid = int(ev["userid"])
        if userid == theMatch.vipID:
            if theMatch.vip.health / VIPHealth < 0.2 and not ev["es_userdead"]:
                es.centertell(theMatch.vipID, "Your health is critically low! Take cover!")
        elif userid == theMatch.assassinID and not ev["es_userdead"]:
            if theMatch.assassin.health / AssassinHealth < 0.2:
                es.centertell(theMatch.assassinID, "Your health is critically low! Take cover!")

        if ev["es_attackerteam"] == ev["es_userteam"] and not ev["userid"] == ev["attacker"]:
            es.centertell(ev["attacker"], "You just shot a friend!")

def player_death(ev):
    if started:
        userid = int(ev["userid"])
        if userid == theMatch.vipID:
            theMatch.assassinWins()

def player_disconnect(ev):
    if started:
        if int(ev["userid"]) == theMatch.vipID:
            theMatch.assassinWins()
        if int(ev["userid"]) == theMatch.assassinID:
            theMatch.aInvisibilityInfo.clear()

def item_pickup(ev):
    if started:
        userid = int(ev["userid"])
        if userid == theMatch.vipID and theMatch.vip.getPrimary():
            theMatch.vip.removePrimary()
            
def es_map_start(ev):
    theMatch.clearAssassinInvisibilityInfo()
