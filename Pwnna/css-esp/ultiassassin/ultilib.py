# +-----------------------------------------------+
# | UltiLib For UltiAssassin                      |
# | filename: ultilib.py                          |
# | Created by Ulti - http://thekks.net           |
# | Status: Internal Uses                         |
# | Version: 0.11                                 |
# | Website: http://thekks.net                    |
# | Requirement: EventScript 2.1 or higher        |
# |              SourcePythonExtension (SPE)      |
# | Generic Module                                |
# +-----------------------------------------------+
# |                    Credits                    |
# | Design: KKSNetwork                            |
# | Coding: Ultimatebuster                        |
# +-----------------------------------------------+

VERSION = 0.11

import es, popuplib, playerlib, weaponlib, gamethread
import spe

import random

def createServerVar(varname, value, notify=False, description="A custom cvar."):
    """ Creates a CVAR
        varname - the name of the variable
        value - the default value
        notify - Notify if changed
    """
    sv = es.ServerVar(varname, value)
    
    if notify:
        es.flags("add", "notify", varname)
    return sv

class EasyPlayer(playerlib.Player):
    """Custom Player Object"""    
    def removePrimary(self):
        """Safely removes the primary weapon"""
        if self.primary:
            weaponindex = spe.getWeaponIndex(self.userid, self.primary)
            if weaponindex:
                spe.removeEntityByIndex(weaponindex)
            if self.secondary:
                es.sexec(self.userid, "use %s" % self.secondary)
            else:
                es.sexec(self.userid, "use weapon_knife")

    def removeSecondary(self):
        """Safely removes the secondary weapon"""
        if self.secondary:
            weaponindex = spe.getWeaponIndex(self.userid, self.secondary)
            if weaponindex:
                spe.removeEntityByIndex(weaponindex)
            if self.primary:
                es.sexec(self.userid, "use %s" % self.primary)
            else:
                es.sexec(self.userid, "use weapon_knife")

    def resetColor(self):
        """Resets the player color"""
        self.setColor(255, 255, 255 ,255)

    def replaceSecondaryWeapon(self, sec_wep):
        """Replace the secondary weapon
        sec_wep - the name of a secondary weapon"""
        validwep = ("weapon_glock", "weapon_usp", "weapon_p228", "weapon_deagle", "weapon_elite", "weapon_fiveseven")
        if sec_wep not in validwep:
            raise TypeError("You must have a valid weapon to switch a secondary weapon")
        else:
            currentsec = self.getSecondary()
            if currentsec:
                if currentsec == sec_wep:
                    return
                self.removeSecondary()
            es.give(self.userid, sec_wep)

    def replacePrimaryWeapon(self, prim_wep):
        """Replace the primary weapon
        prim_wep - the name of a primary weapon"""
        validwep = tuple(weaponlib.getWeaponList("#primary"))
        if prim_wep not in validwep:
            raise TypeError("You must have a valid weapon to switch a secondary weapon")
        else:
            currentprim = self.getPrimary()
            if currentprim:
                if currentprim == prim_wep:
                    return
                self.removePrimary()
            es.give(self.userid, prim_wep)

    def giveSmoke(self, amount):
        """Gives smoke grenade to player
        amount - the amount of smoke grenade in integer"""
        self.sg = amount
        if amount > 0:
            es.give(self.userid, "weapon_smokegrenade")

    def giveFlash(self, amount):
        """Gives flash bang to player
        amount - the amount of flashbangs"""
        self.fb = amount
        if amount > 0:
            es.give(self.userid, "weapon_flashbang")

    def giveHE(self, amount):
        """Gives he grenade to player
        amount - the amount of he grenades"""
        self.he = amount
        if amount > 0:
            es.give(self.userid, "weapon_hegrenade")

    def switchTeam(self, teamnum, tmodel="player/t_arctic.mdl", ctmodel="player/ct_gign.mdl"):
        """switch player's team without killing the player
        It will also change the player's model, and move them to their spawn point.
        teamnum - the team number. 2 - Terrorist; 3 - CT; 1 - Spectator
        tmodel - the model of terrorist to change to. Default: player/t_arctic.mdl
        ctmodel - the model of counter terrorist to change to. Default: player/ct_gign.mdl"""
        spe.switchTeam(self.userid, teamnum)
        if teamnum == 2:
            self.moveToSpawn(2)
            self.model = tmodel
        elif teamnum == 3:
            self.moveToSpawn(3)
            self.model = ctmodel

    def moveToSpawn(self, team):
        """Move a player to a spawn point.
        Will also activate noblock on the player in case where 2 player spawn on the same place.
        Deactivates no block in 5 + mp_freezetime
        team - the team number. 2 - Terrorist; 3 - CT"""
        spawnLocations = getSpawnLocations(team)
        if spawnLocations:
            spawnloc = random.choice(spawnLocations)
            es.setpos(self.userid, spawnloc[0], spawnloc[1], spawnloc[2])
            self.noblock(1)
            delaytime = es.ServerVar("mp_freezetime") + 5
            gamethread.delayed(delaytime, self.noblock, (0, ))
    
    def suicide(self):
        """Make the player commit suicide"""
        es.sexec(self.userid, "kill")
    
    def unblind(self):
        """Unblinds a player"""
        self.flash(0, 10)
        
##############################
#### Standalone Functions ####
##############################

def removeMapObjective(bomb=True, hostage=True, buyzone=True, userid=None):
    """ Removes Map Objective.
    bomb - Defines whether to remove bomb objective or not. Default: True
    hostage - Defines whether to remove hostage objective or not. Default: True
    buyzone - Defines whether to remove buying objective or not. Default: True
    userid - A userid for es.fire to use. If not provided (None), the first lowest userid in the game will be used.
    """
    hostageEntity = ('func_hostage_rescue', 'hostage_entity')
    bombEntity = ('func_bomb_target', 'weapon_c4') 
    if userid == None:
        userid = es.getUseridList()[0]
    if bomb:
        for entity in bombEntity:
            es.fire(userid, entity, "Kill")
            
    if hostage:
        for entity in hostageEntity:
            es.fire(userid, entity, "Kill")
    
    if buyzone:
        es.fire(userid, "func_buyzone", "Kill")

def getSpawnLocations(team):
    """Gets the spawn location using entities. Put them in a tuple and return them.
    team - the team number. 2 - Terrorist; 3 - CT"""
    if team == 2:
        tSpawnEntities = es.createentitylist("info_player_terrorist")
        locations = []
        for key in tSpawnEntities:
            xyz = tuple(tSpawnEntities[key]["CBaseEntity.m_vecOrigin"].split(","))
            locations.append(xyz)
        return tuple(locations)
    elif team == 3:
        ctSpawnEntities = es.createentitylist("info_player_counterterrorist")
        locations = []
        for key in ctSpawnEntities:
            xyz = tuple(ctSpawnEntities[key]["CBaseEntity.m_vecOrigin"].split(","))
            locations.append(xyz)
        return tuple(locations)
    else:
        return False
        

class WeaponSelectionMenu(object):
    """Weapon selection menu"""
    def __init__(self, userid, weaponslist):
        if playerlib.getPlayer(userid).isbot:
            es.give(userid, "weapon_" + weaponslist[0])
            return None
            
        if len(weaponslist) == 1:
            es.give(userid, "weapon_" + weaponslist[0])
            return None
        
        self.userid = userid
        self.weaponslist = weaponslist
        menuid = random.randint(0, 1000)
        if es.exists("popup", "ultilib_weaponmenu%d" % menuid):
            popuplib.delete("ultilib_weaponmenu%d" % menuid)
            
        weaponMenu = popuplib.create("ultilib_weaponmenu%d" % menuid)
        weaponMenu.addline("Choose a weapon:")
        weaponMenu.addline(" ")
        if len(self.weaponslist) < 9:
            for i in range(0, len(self.weaponslist)):
                weaponMenu.addline("->%d. %s" % (i+1, self.weaponslist[i]))
        else:
            for i in range(0, 9):
                weaponMenu.addline("->%d. %s" % (i+1, self.weaponslist[i]))
        
        weaponMenu.addline(" ")
        weaponMenu.addline("0. Cancel")
        weaponMenu.menuselect = self.select

        popuplib.send("ultilib_weaponmenu%d" % menuid, userid)

    def select(self, userid, choice, popupid):
        if choice < 11:
            es.give(userid, "weapon_" + self.weaponslist[choice-1])
        
