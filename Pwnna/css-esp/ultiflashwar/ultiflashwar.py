# +-----------------------------------------------+
# | UltiFlashWar v1.0                             |
# | filename: ultiflashwar.py                     |
# | Created by Ulti - http://thekks.net           |
# | Status: Release                               |
# | Website: http://thekks.net                    |
# | Requirement: EventScript 2.1 or higher        |
# |              SPE (SourcePythonExtension)      |
# |              UltiLib 0.11 (Included)          |
# +-----------------------------------------------+
# |                    Credits                    |
# | Design: KKSNetwork                            |
# | Coding: Ultimatebuster                        |
# +-----------------------------------------------+

import es, playerlib, spe
import ultilib

def round_start(ev):
    es.centermsg("FLASHBANG WAR!")
    es.msg("#multi", "#green[UltiFlashWar 1.0]#defaultYou're playing the the flashbang war mod by Ulti")

def player_spawn(ev):
    if int(ev["es_userteam"]) > 1:
        player = ultilib.EasyPlayer(ev["userid"])
        player.cash = 0
        player.health = 1
        player.giveFlash(1000)
        player.nightvision = 1
        player.removeSecondary()
        player.removePrimary()
        es.sexec(player.userid, "use weapon_flashbang")
        if int(ev["es_userteam"]) == 3:
            player.defuser = 1
    
def player_blind(ev):
    ultilib.EasyPlayer(ev["userid"]).unblind()

def load():
    spe.registerPreHook('player_hurt', before_player_hurt)
    
def unload():
    es.msg("#multi", "#green[UltiFlashWar 1.0]#defaultUltiFlashWar has been unloaded. Use 'changelevel %s' to restore map objectives!" % str(es.ServerVar("eventscripts_currentmap")))
    
def before_player_hurt(ev):
    if ev["weapon"] != "flashbang":
        ultilib.EasyPlayer(ev["userid"]).health = 1
        es.centertell(ev["attacker"], "USE FLASHBANG ONLY!")
