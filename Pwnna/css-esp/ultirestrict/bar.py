""" Addon Information """
# ------------
# EventScripts Script-Addon:    BackRaw's AWP-Restrict (BAR, bar.py, 7.6kb)
# Author:                       BackRaw - http://forums.eventscripts.com/profile.php?mode=viewprofile&u=13683
#                                         http://addons.eventscripts.com/addons/user/13683
# Version:                      1.1
# ------------

""" Imports """
# ------------
# EventScripts Core-Module                - ES-functionality
import es
# Popuplib                                - Popup menus
from popuplib import create as popup
# Config Object                           - Configuration File: ./addons/eventscripts/bar/bar_config.ini
from configobj import ConfigObj
# ------------

""" Global Variables """
# ------------
# This variable will hold the Prefix of BAR.
# We'll need the same string often, a global variable is the best for that.
prefix = "#green[#lightgreenBackRaw's AWP-Restrict#green] #default"
# ------------

""" Configuration File wrapper """
def config(name=False, section=False):
    f = ConfigObj(es.getAddonPath('bar') + '/bar_config.ini')
    if name:
        if name not in ['admins', 'saycommand']:
            if section:
                return int(f[section][name])
            return int(f[name])
        return f[name]
    return f

""" Class - AWP """
# ------------
# This class holds allowed and counted AWPs for CT and T.
# If a player picks up an AWP, it drops the player's AWP when the allowed AWP-count is already reached.
# It also contains buy-restriction, console-buy, too.
# ------------
class AWP(object):
    def __init__(self):
        self.count_t = self.count_ct = 0
        self.allowed_t = self.allowed_ct = 0
        self.rcount = 0
    def roundStart(self):
        count = es.getplayercount()
        allowed = []
        for key in config()['restriction']:
            if key != 'more':
                allowed.append(int(key))
            else:
                allowed.append(key)
        i = 0
        for c in allowed:
            if count <= c or (count > c and count < allowed[i + 1]):
                count = self.allowed_ct = self.allowed_t = config(str(c), 'restriction')
                break
            i += 1
        self.count_ct = self.count_t = 0
        if config('announce'):
            self.rcount += 1
            if self.rcount in [1, 3]:
                es.msg('#multi', '%sYou can use #lightgreen%s #greenAWP%s #defaultper team.' % (prefix, count, 's' if count > 1 else ''))
                self.rcount = 0
    def dontAllow(self, userid, index):
        team = es.getplayerteam(userid)
        es.server.cmd('es_xremove %s' % index)
        if config('pickup'):
            es.tell(userid, '#multi', '%sYou cannot pickup this #greenAWP #lightgreen- %s/%s #defaultAWPs in use.' % (prefix, self.count_t if team == 2 else self.count_ct, self.allowed_t if team == 2 else self.allowed_ct))
        es.sexec(userid, 'use slot2')
    def awpPickup(self, userid, index):
        team = es.getplayerteam(userid)
        if team == 2:
            if self.count_t >= self.allowed_t:
                self.dontAllow(userid, index)
            else:
                self.count_t += 1
        elif team == 3:
            if self.count_ct >= self.allowed_ct:
                self.dontAllow(userid, index)
            else:
                self.count_ct += 1
    def awpBuy(self, team):
        allow = 1
        if team == 2 and self.count_t >= self.allowed_t or team == 3 and self.count_ct >= self.allowed_ct:
            allow = 0
        return allow
    def awpDrop(self, team):
        if team == 2 and self.count_t:
            self.count_t -= 1
        elif team == 3 and self.count_t:
            self.count_ct -= 1
awp = AWP()

""" Events """
# ------------
# On round_start, re-allow AWP-counts.
# ------------
def round_start(ev):
    awp.roundStart()

# ------------
# On item_pickup - if the item is AWP - remove the AWP or let the player pick it up.
# ------------
def item_pickup(ev):
    if ev['item'] == 'awp':
        index = 0
        userid = ev['userid']
        handle = es.getplayerhandle(userid)
        for x in es.createentitylist('weapon_awp'):
            if es.getindexprop(x, 'CBaseEntity.m_hOwnerEntity') == handle:
                index = x
        awp.awpPickup(userid, index)

# ------------
# On player_death, count the AWP-count for the team down, if the player had an AWP.
# ------------
def player_death(ev):
    _awp = 0
    for x in es.createentitylist('weapon_awp'):
        if es.getindexprop(x, 'CBaseEntity.m_hOwnerEntity') == -1:
            _awp = 1
    if _awp:
        awp.awpDrop(int(ev['es_userteam']))

""" Client Command Filter """
# ------------
# This checks buy and drop-commands, and calls the functions in the AWP-class.
# ------------
def clientFilter(userid, args):
    cmd = args[0].lower()
    if cmd in ['buy', 'drop']:
        team = es.getplayerteam(userid)
        weapon = es.createplayerlist(userid)[int(userid)]['weapon'].replace('weapon_', '')
        if cmd == 'buy':
            buy = args[1].lower()
            if 'awp' in buy and not awp.awpBuy(team):
                if config('buy'):
                    es.tell(userid, '#multi', '%sYou cannot buy this #greenAWP #lightgreen- %s/%s #defaultAWPs in use.' % (prefix, awp.count_t if team == 2 else awp.count_ct, awp.allowed_t if team == 2 else awp.allowed_ct))
                return False
            elif 'awp' not in buy and weapon == 'awp':
                awp.awpDrop(team)
        elif cmd == 'drop' and weapon == 'awp':
            awp.awpDrop(team)
    return True

""" Say-Filter """
# ------------
# Admin Menu options
# ------------
def sayFilter(userid, text, teamonly):
    def modLines(arg):
        menu.modline(7, '%s1. Announcements: %s' % (arg, config('announce')))
        menu.modline(8, '%s2. Pickup-Telling: %s' % (arg, config('pickup')))
        menu.modline(9, '%s3. Buy-Telling: %s' % (arg, config('buy')))
    def adminSelect(userid, choice, popupid):
        if choice in [1, 2, 3]:
            f = ConfigObj(es.getAddonPath('bar') + '/bar_config.ini')
            if choice == 1:
                if config('announce'):
                    f['announce'] = '0'
                else:
                    f['announce'] = '1'
            elif choice == 2:
                if config('pickup'):
                    f['pickup'] = '0'
                else:
                    f['pickup'] = '1'
            elif choice == 3:
                if config('buy'):
                    f['buy'] = '0'
                else:
                    f['buy'] = '1'
            f.write()
            modLines('->')
            menu.send(userid)
    text = text.strip('"')
    if text == config('saycommand'):
        if es.getplayersteamid(userid) in config('admins'):
            modLines('->')
            menu.menuselect = adminSelect
        else:
            menu.menuselect = 0
            modLines('')
        menu.send(userid)
        return (None, None, None)
    return (userid, text, teamonly)

""" EventScripts Main-Control functions """
# ------------
# On load, register a Client Console-Command Filter and re-allow AWP-counts.
# ------------
def load():
    global menu
    es.ServerVar('bar_ver', '1.0').makepublic()
    es.addons.registerSayFilter(sayFilter)
    es.addons.registerClientCommandFilter(clientFilter)
    awp.roundStart()

# ------------
# On unload, un-register the Client Console-Command Filter.
# ------------
def unload():
    es.addons.unregisterSayFilter(sayFilter)
    es.addons.unregisterClientCommandFilter(clientFilter)

""" End Code """
