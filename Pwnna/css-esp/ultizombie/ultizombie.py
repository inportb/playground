# +-----------------------------------------------+
# | UltiZombie v1.1                               |
# | filename: ultizombie.py                       |
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
# | Zombie Model: DEN_999                         |
# +-----------------------------------------------+

# Changelog:
# ---0.1---
# First working version
# ---0.2---
# First Private Release
# More features + bugs fix
# ---0.3---
# More features + bugs fix
# ---0.4---
# Initial Public Release
# Completely Rewritten the script in Python
# Code Optimization
# ---0.5---
# Included Zombie Model by DEN_999
#   Original Model found here: 
#   http://www.zombiemod.com/forums/downloads.php?do=file&id=172
# Better Config Instructions
# ---0.6---
# Added weapon select menu
# Fixed the archive structure
# ---1.0---
# Complete rewrite using object oriented approach
# ---1.1---
# Fixed bugs

# Configurations #
noMapObjective = 0              # If set to 1, there will be no map objective, bomb and hostage will be removed from the game. Default: 0
additionalHealth = 10           # The health to add when a human kills a bot. Default: 10

humanHealth = 100               # The health human players spawns with. Default: 100
botHealth = 1500                # The health of bot (zombie) players spawns with. Default: 1000

grenadeDmgMultiplier = 50.0     # 0 disables grenades, Other values are dmg multipliers. Default: 50.0
selectWeapon = 1                # 0 disables the weapon selection menu that the player gets at spawn, otherwise the message will be on the ground arround the player. Default: 1

useZombieModel = 1              # 0 disables the zombie model, only uses the regular ones. Default: 1

weaponsToGive = ("mp5navy",
                 "ak47",
                 "m3",
                 "m249",
                 "aug",
                 "m4a1")        # The list of weapons to give. To customize you need to add a , and then "<weaponnamehere>" inside the brackets.
# Configurations #

######## DO NOT MODIFY ANYTHING BEYOND THIS LINE ########
###### UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING! ######



import es, playerlib, weaponlib, usermsg
import spe

import ultilib

info = es.AddonInfo()
info.name         = "UltiZombie"
info.version      = "1.1"
info.author       = "Ulti"
info.description  = "A single player/coop zombie mod"
info.url          = "http://addons.eventscripts.com/addons/view/ultizombie"
info.basename     = "ultizombie"

changed = False

class Zombie(ultilib.EasyPlayer):
    def prepare(self):
        self.health = int(es.ServerVar("uz_bothealth"))
        if useZombieModel:
            self.setModel("models/player/home net server/zombie/zombie_hc/t_arctic.mdl")
        self.cash = 0

class Human(ultilib.EasyPlayer):
    def prepare(self):
        if int(es.ServerVar("uz_select")):
            ultilib.WeaponSelectionMenu(self.userid, weaponsToGive)
        else:
            for weapon in weaponsToGive:
                es.give(self.userid, "weapon_%s" % weapon)
                
        if self.teamid == 3:
            self.defuser = 1
        
        if int(es.ServerVar("uz_grenade")) > 0:
            self.giveHE(1)
            
        self.nightvision = 1
        es.give(self.userid, "item_assaultsuit")
        self.health = int(es.ServerVar("uz_humanhealth"))
        self.cash = 16000
        
class ZombieModMatch(object):
    def __init__(self):
        self.humans = {}
        self.bots = {}
        
    def playerSpawn(self, ev):
        if int(ev["es_userteam"]) > 1:
            userid = int(ev["userid"])
            if es.isbot(userid):
                self.bots[userid] = Zombie(userid)
                self.bots[userid].prepare()
            else:
                self.humans[userid] = Human(userid)
                self.humans[userid].prepare()
    
    def playerHurt(self, ev):
        if int(ev["attacker"]) in self.humans:
            if ev['weapon'] == "hegrenade" and int(ev["userid"]) in self.bots:
                dmg = int(float(ev["dmg_health"]) * float(es.ServerVar("uz_grenade")))
                usermsg.hudhint(ev["attacker"], "Damages: %s" % str(dmg)) # Display Damage
            else:
                usermsg.hudhint(ev["attacker"], "Damages: %s" % ev["dmg_health"]) # Display Damage
    
    def roundStart(self, ev):
        global changed
        if not changed:
            limitteams = es.ServerVar("mp_limitteams")
            autobalance = es.ServerVar("mp_autoteambalance")
            es.server.queuecmd("bot_knives_only")
            if limitteams < 15:
                limitteams.set(20)

            if autobalance == 1:
                autobalance.set(0)
            changed = True
        
        if noMapObjective:
            ultilib.removeMapObjective(buyzone=False)
            es.centermsg("Kill the zombies and survive!!")
        
        es.msg("#multi", "#green[UltiZombie 1.0]#defaultYou're playing the single player/coop zombie mod by Ulti")
        es.centermsg("Do your objective or kill all zombies!")
    
    def hostageFollows(self, ev):
        es.centermsg("%s is rescuing the hostages" % ev["es_username"])
    
    def bombBeginPlant(self, ev):
        es.centermsg("%s is planting the bomb!" % ev["es_username"])
    
    def roundEnd(self, ev):
        if int(ev["reason"]) == "1":
            pass
            
        self.humans = {}
        self.bots = {}
    
    def playerDeath(self, ev):
        if es.isbot(ev["userid"]) and not es.isbot(ev["attacker"]):
            self.humans[int(ev["attacker"])].health += int(es.ServerVar("uz_healthadd"))
        elif not es.isbot(ev["userid"]):
            es.centermsg("%s was killed in action!" % ev["es_username"])
            

    def beforePlayerHurt(self, ev):
        attacker = int(ev["attacker"])
        victim = int(ev["userid"])       
        
        if attacker != victim and attacker in self.humans and victim in self.bots and ev["weapon"] == "hegrenade" and int(es.ServerVar("uz_grenade")) > 0:
            damage = int(ev["dmg_health"]) * (float(es.ServerVar("uz_grenade")) - 1)
            self.bots[victim].health -= damage
        elif ev["weapon"] == "knife" and attacker in self.bots and victim in self.humans:
            damage = int(ev["dmg_health"]) * 3.0
            self.humans[victim].health -= damage
            
    
    def setdownloadables(self):
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.xbox.vtx")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.vvd")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.sw.vtx")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.phy")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.mdl")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.dx90.vtx")
        es.stringtable("downloadables", "models/player/home net server/zombie/zombie_hc/t_arctic.dx80.vtx")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/Zombie_Classic_sheet_normal.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/Zombie_Classic_sheet.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/Zombie_Classic_sheet.vmt")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/t_leet_normal.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/t_leet.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/t_leet.vmt")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/headcrabsheet_normal.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/headcrabsheet.vtf")
        es.stringtable("downloadables", "materials/models/player/home net server/zombie/zombie_hc/headcrabsheet.vmt")
        
theround = ZombieModMatch()

def load():
    spe.registerPreHook('player_hurt', theround.beforePlayerHurt)
    ultilib.createServerVar("uz_healthadd", additionalHealth, True)
    ultilib.createServerVar("uz_humanhealth", humanHealth, True)
    ultilib.createServerVar("uz_bothealth", botHealth, True)
    ultilib.createServerVar("uz_grenade", grenadeDmgMultiplier, True)
    ultilib.createServerVar("uz_select", selectWeapon, True)    
    theround.setdownloadables()

def es_map_start(ev):
    global changed
    changed = False
    theround.setdownloadables()
    
def round_start(ev):
    theround.roundStart(ev)
    
def player_spawn(ev):
    theround.playerSpawn(ev)
    
def player_hurt(ev):
    theround.playerHurt(ev)
    
def hostage_follows(ev):
    theround.hostageFollows(ev)
    
def bomb_beginplant(ev):
    theround.bombBeginPlant(ev)

def player_death(ev):
    theround.playerDeath(ev)
    
def round_end(ev):
    theround.roundEnd(ev)
