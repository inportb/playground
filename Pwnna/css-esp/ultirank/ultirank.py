# +-----------------------------------------------+
# | UltiRank v0.21                                |
# | filename: ultirank.py                         |
# | Created by Ulti - http://thekks.net           |
# | Status: Beta                                  |
# | Website: http://thekks.net                    |
# | Requirement: EventScript 2.1 or higher        |
# +-----------------------------------------------+
# |                    Credits                    |
# | Design: KKSNetwork                            |
# | Coding: Ultimatebuster                        |
# +-----------------------------------------------+

method = "steam"        # ip will be using ip to identify
                        # steam will be using steam id to identify
                        # name will be using name to identify
                        # if you reset this, you need delete the previous database.
                    
botKillsCounts = 0      # 1 then bot kills counts as points, 0 and bot kills don't count as points
                        # Bot does not get ranked
tkPointsDecrease = 4    # The points decrease when you tk or suicide
killPointsIncrease = 2  # The points increase when you kill someone
deathPointsDecrease = 2 # The points decrease when you die
resetRankPer = 0        # Every x hour, the user can reset their rank. (If set to 0, users cannot reset rank.)
headshotExtraPoints = 0 # The points extra if it's a headshot

################################################################################
################################################################################
#####################DO NOT CHANGE ANYTHING BELOW THIS LINE#####################
################################################################################
################################################################################


import es, playerlib, popuplib, usermsg, cmdlib

import shelve, shutil

import urllib2, time

info = es.AddonInfo()
info.name         = "UltiRank"
info.version      = "0.21 Beta"
info.author       = "Ulti"
info.description  = "A simple ranking script"
info.url          = "http://addons.eventscripts.com/addons/view/ultirank"
info.basename     = "ultirank"

method = method.lower()

currentversion = 0.21
dbversion = 0.2

class RankingSystem(object):
    """ Create a ranking system class """
    def __init__(self):
        """ Opens the database, check if the database is valid """
        # Opens the database
        es.ServerVar("ultirank_version", info.version, "UltiRank version number").makepublic()
        self.ranksData = shelve.open(es.getAddonPath("ultirank") + "/rankdata.db", writeback=True)
        # Assume readonly is false.
        self.readonly = False
        
        # Assume not out of date
        self.outOfDate = False
        
        # Check for the type of identification method from the database, verify against the setting.
        if self.ranksData.has_key("method"):
            self.identifyMethod = self.ranksData["method"]
            if self.identifyMethod != method:
                # If they don't match, activates read only and displays error.
                self.activateReadOnly()
                es.dbgmsg(0, "ERROR: Identification method has been changed. Previous method is %s, current is %s. Please delete the old database to restart logging, or change the identification method back." % (self.identifyMethod, method.lower()))
                return
        else:
            # If there's no method, it's likely a new database, set it.
            self.ranksData["method"] = method
            self.identifyMethod = self.ranksData["method"]
        
        # Check for database version
        if self.ranksData.has_key("version"):
            self.actualdbversion = self.ranksData["version"]
            if self.actualdbversion < dbversion:
                # if the db version is older, upgrade must be performed. Readonly set.
                self.activateReadOnly()
                es.dbgmsg(0, "ERROR: Database must be upgraded to the latest version! Type ultirank_upgrade to perform the upgrade.")
            elif self.actualdbversion > dbversion:
                # If the db version is newer, give a warning, and attempt to continue, very risky.
                es.dbgmsg(0, "WARNING: UltiRank is outdated as your database version is higher. You might need to download a newer version.")
        else:
            # If there's no version key, it's likely a new database, initialize it
            # ??: Problem here?
            self.ranksData["version"] = dbversion
            self.actualdbversion = self.ranksData["version"]
            
        self.checkUpdate()
        
        # Cache the ranking data
        self.initData()
        # If no errors occured, display message.
        if not self.readonly:
            self.showInfo()
            
    def showInfo(self, args=None):
        self.showCheckedUpdate()
        es.dbgmsg(0, "[UltiRank] UltiRank %s has been loaded!" % info.version)
        es.dbgmsg(0, "[UltiRank] UltiRank DB Version: %.2f" % self.actualdbversion)
        es.dbgmsg(0, "[UltiRank] UltiRank Identify Method: %s" % self.identifyMethod)
        es.dbgmsg(0, "[UltiRank] UltiRank currently had %d players on file!" % len(self.ranklist))
        es.dbgmsg(0, "[UltiRank] UltiRank created by ultimatebuster. http://thekks.net")
            
    def activateReadOnly(self):
        """ Activates the read only mode for the data """
        # Caches the data, close the database, set readonly.
        if self.readonly:
            return
        
        self.initData()
        self.close()
        self.readonly = True
        es.dbgmsg(0, "WARNING: Ranking system is now in read only mode!")
        
    def allowedResetRank(self, userid):
        lastResetTime = self.ranksData[self.identifyPlayer(userid)]["resettime"]
        resetPerSec = float(es.ServerVar("ultirank_user_reset_per")) * 3600
        now = time.time()
        if resetPerSec:
            if now - resetPerSec > lastResetTime:
                return True
        return False
    
    def resetRank(self, userid):
        if not self.readonly:
            if self.allowedResetRank(userid):
                self.setRankDataToZero(userid)
                self.tellplayer(userid, "Your rank has been reset to 0!");
            else:
                hour = int(es.ServerVar("ultirank_user_reset_per"))
                if hour:
                    self.tellplayer(userid, "You are not allowed to reset now! You may only every %d hours." % hour)
        else:
            self.tellplayer(userid, "You are not allowed to reset now!")
        
    def identifyPlayer(self, userid):
        """ Give player a unique identifier given the identify method in the db """
        userid = int(userid)
        player = playerlib.Player(userid)
        # If the player is a bot, return the "BOT unique id"
        if player.isbot:
            return "BOT"
        
        # If the identify method is nothing, return the player's ip address.
        if self.identifyMethod == "ip":
            return player.address
        elif self.identifyMethod == "steam":
            return player.steamid
        elif self.identifyMethod == "name":
            return player.name
        else:
            return player.address
        
    def setRankDataToZero(self, userid):
        uniqueid = self.identifyPlayer(userid)
        self.ranksData[uniqueid] = {"name" : str(playerlib.getPlayer(userid).name), 
                                        "points" : 0, 
                                        "kills" : 0, 
                                        "deaths" : 0,
                                        "resettime" : time.time()}
        
    def initPlayer(self, userid):
        """ Initialize the player in the db """
        # If it is ready only, stops storing the player db
        if self.readonly:
            return False
        
        userid = int(userid)
        uniqueid = self.identifyPlayer(userid)
        # if it's a bot, stops storing the player into the db
        if uniqueid == "BOT":
            return
        
        # If the database doesn't have a key for that unique id, it's probably a new player.
        # initialize him with 0 points, 0 death, 0 kills.
        if not self.ranksData.has_key(uniqueid):
            self.setRankDataToZero(userid)
        else:
            # Otherwise, refresh the name of the player.
            self.ranksData[uniqueid]["name"] = str(playerlib.getPlayer(userid).name)
    
    def tellplayer(self, userid, msg):
        """ es.tell's wrapper, where [UltiRank version] is printed at the front """
        es.tell(userid, "#multi", "#green[UltiRank %s] #default%s" % (info.version, str(msg)))
    
    def getSortedPoints(self, limit=0):
        """ Get a tuple of the sorted rank (highest first) """
        sortedRankList = []
        for uniqueid in self.ranksData:
            if uniqueid == "method" or uniqueid == "version":
                continue
            sortedRankList.append((self.ranksData[uniqueid]["points"], 
                                   self.ranksData[uniqueid]["kills"],
                                   self.ranksData[uniqueid]["deaths"],
                                   self.ranksData[uniqueid]["name"],
                                   uniqueid))
        # done via built in tuple sort thing, where it compares the tuple's value, one by one.
        sortedRankList.sort()
        sortedRankList.reverse()
        # if a positive limit is specified, return it.
        if limit > 0 and limit < len(sortedRankList):
            return tuple(sortedRankList[0:limit])
        else:
            return tuple(sortedRankList)
    
    def getPersonalRank(self, uniqueid):
        """ Get the rank of a player, and all info regarding the player. """
        personalRank = []
        # ??: Brute force search. Not efficient.
        for i in range(len(self.ranklist)):
            if self.ranklist[i][4] == uniqueid:
                personalRank.append(i+1)
                personalRank.extend(self.ranklist[i])
                break
        
        return personalRank
    
    def announcePersonalRank(self, userid):
        """ Announce the personal rank """
        playerRank = self.getPersonalRank(self.identifyPlayer(userid))
        es.msg("%s is ranked %d of %d with %d points. Kills: %d Deaths: %d KDR: %s" % (playerlib.Player(userid).name, playerRank[0], len(self.ranklist), playerRank[1], playerRank[2], playerRank[3], self.getKDR(playerRank[2], playerRank[3])))
        if self.readonly:
            self.tellplayer(userid, "The ranking system is currently in read-only mode. Your kills and deaths will not be logged.")
        
    
    
    def tellPersonalRank(self, userid):
        """ Use a popup to display the rank """
        popupName = "ultirank_rank_%s" % str(userid)
        playerRank = self.getPersonalRank(self.identifyPlayer(userid))
        if popuplib.exists(popupName):
            popuplib.delete(popupName)
        rpopup = popuplib.create(popupName)
        rpopup.addline(playerlib.Player(userid).name)
        rpopup.addline("================")
        rpopup.addline("Rank: %d of %d" % (playerRank[0], len(self.ranklist)))
        rpopup.addline("Points: %d" % playerRank[1])
        rpopup.addline("Kills: %d" % playerRank[2])
        rpopup.addline("Deaths: %d" % playerRank[3])
        rpopup.addline("KDR: %s" % self.getKDR(playerRank[2], playerRank[3]))
        rpopup.addline(" ")
        rpopup.addline("0. Close")
        rpopup.send(userid)
        if self.readonly:
            self.tellplayer(userid, "The ranking system is currently in read-only mode. Your kills and deaths will not be logged.")
    
    def getKDR(self, kills, deaths):
        """ Get the KDR, really it's just a division wrapper"""
        try:
            kdr = "%.2f" % (float(kills) / deaths)
        except ZeroDivisionError:
            kdr = "Undefined"
        return kdr
    
    def getTop10Popup(self):
        """ Returns a popup that has the top10 player's info populated """
        if len(self.ranklist) >= 10:
            top10 = self.ranklist[0:10]
        else:
            top10 = self.ranklist # Potential referencing issue
        if popuplib.exists("ultirank_top10"):
            popuplib.delete("ultirank_top10")
        rankPopup = popuplib.create("ultirank_top10")
        rankPopup.addline("[UltiRank %s] Top 10" % info.version)
        rankPopup.addline("=================================")
        for i in range(len(top10)):
            rankPopup.addline("%d. %s: %d points (KDR: %s)" % (i+1, top10[i][3], top10[i][0], self.getKDR(top10[i][1], top10[i][2])))
        rankPopup.addline(" ")
        rankPopup.addline("0. Close")
        return rankPopup
    
    def sendTop10Popup(self, userid):
        """ Sends the top10 popup when called """
        self.getTop10Popup().send(userid)
        if self.readonly:
            self.tellplayer(userid, "The ranking system is currently in read-only mode. Your kills and deaths will not be logged.")
    
    def initData(self):
        """ Caches a copy of the rank from the database to improve efficiency """     
        self.showCheckedUpdate()
        if not self.readonly:
            self.ranksData.sync()
            self.ranklist = self.getSortedPoints()
            self.top10popup = self.getTop10Popup()
        else:
            es.dbgmsg(0, "WARNING: Ranking system is now in read only mode!")
        
    def close(self):
        """ Closes the db """
        self.ranksData.close()
    
    def enable(self, args):
        """ Handles the console command that can enable/disables the rank (enter readonly mode) 
            Correct command usage is ultirank_enable 1 or ultirank_enable 0"""
        if len(args) == 1:
            if int(args[0]) == 1 and self.readonly:
                self.__init__()
            elif int(args[0]) == 0 and not self.readonly:
                self.activateReadOnly()
            else:
                es.dbgmsg(0, "Correct usage of this command is ultirank_enable <0/1>")
        else:
            es.dbgmsg(0, "Correct usage of this command is ultirank_enable <0/1>")
            
    def upgradedb(self, args):
        """ Handles the console command that upgrades the databse
            Correct command usage is ultirank_upgrade """
        # Imports the upgrader and activateReadOnly
        try:
            import upgrader
        except ImportError:
            es.dbgmsg(0, "ERROR: Upgrader cannot be found! It either means you don't need any upgrade, or you lost the upgrader somehow. If your answer is the latter, you need to download a new copy of the script.")
            return
            
        self.activateReadOnly()
        # The return status tells us how the upgrade went. The script gives the dbversion it wants, and the location of the db
        returnStatus = upgrader.upgrade(dbversion, es.getAddonPath("ultirank") + "/rankdata.db")
        if returnStatus == -1:
            es.dbgmsg(0, "ERROR: Some problem has occurred while upgrading.")
        elif returnStatus == upgrader.TO_VERSION_MISMATCH:
            es.dbgmsg(0, "ERROR: The upgrader only upgrades to version %.2f while you're requesting to upgrade to %.2f" % (upgrader.to_version, dbversion))
        elif returnStatus == upgrader.FROM_VERSION_MISMATCH:
            es.dbgmsg(0, "ERROR: The upgrader only upgrades database version of %.2f while your db has a version of %.2f" % (upgrader.from_version, self.actualdbversion))
        elif returnStatus == upgrader.DB_ALREADY_UPTODATE:
            es.dbgmsg(0, "Database are already up to date. Re-enabling UltiRank...")
            self.__init__()
        elif returnStatus == 0:
            # if the db upgrade works, re-enable the rank by completely reinitialze it.
            es.dbgmsg(0, "Database update complete. Re-enabling UltiRank...")
            self.__init__()
    
    def showCheckedUpdate(self):
        if self.outOfDate:
            es.dbgmsg(0, "ERROR: UltiRank is out of date. The newest version is %.2f. You're running version %.2f." % (self.outOfDate, currentversion))
            es.dbgmsg(0, "Please update by downloading the latest copy at %s" % info.url)
        elif self.outOfDate == None:
            es.dbgmsg(0, "WARNING: UltiRank cannot check for update.")
    
    def checkUpdate(self):
        self.outOfDate = self.checkForUpdate("http://thekks.net/checkupdate.php?product=ultirank", currentversion)
            
    def checkForUpdate(self, location, currentversion):
        try:
            v = urllib2.urlopen(location).readline().strip()
            v = float(v)
            if v > currentversion:
                return v
            else:
                return False
        except (ValueError, IOError, urllib2.URLError, urllib2.HTTPError):
            return None
    
    def addKill(self, uniqueid, kill=1, points=None, headshot=False):
        """ Adds a kill """
        if points == None:
            points = int(es.ServerVar("ultirank_kill_points_increase"))
            
        if headshot:
            points += int(es.ServerVar("ultirank_headshot_extra"))
            
        self.ranksData[uniqueid]['kills'] += kill
        self.ranksData[uniqueid]['points'] += points
        return points
        
    def addDeath(self, uniqueid, death=1, points=None):
        if points == None:
            points = int(es.ServerVar("ultirank_death_points_decrease")) 
            
        self.ranksData[uniqueid]["deaths"] += death
        self.ranksData[uniqueid]["points"] -= points
        return points
    
    def playerDeath(self, ev):
        """ Player death event, where most awesome stuff happens """
        if self.readonly:
            return False
        
        attackerUniqueID = self.identifyPlayer(ev["attacker"])
        victimUniqueID = self.identifyPlayer(ev["userid"])
        if ev["es_userteam"] == ev["es_attackerteam"]:
            if attackerUniqueID == "BOT":
                return
            
            # needs refactoring
            decreasedPoints = int(es.ServerVar("ultirank_tk_points_decrease"))
            if ev["userid"] == ev["attacker"]:
                self.addKill(victimUniqueID, -1, 0)
                self.addDeath(victimUniqueID, points=decreasedPoints)
                self.tellplayer(ev["userid"], "You suicided! You've lost %d points." % decreasedPoints)
            else:
                self.addKill(attackerUniqueID, -1, decreasedPoints*-1)
                self.tellplayer(ev["attacker"], "You killed a team mate! You've lost %d points." % decreasedPoints)
        else:
            if victimUniqueID == "BOT" and attackerUniqueID == "BOT":
                return 
            
            if (victimUniqueID == "BOT" or attackerUniqueID == "BOT") and not int(es.ServerVar("ultirank_botcount")):
                return
            
            if victimUniqueID == "BOT" and int(es.ServerVar("ultirank_botcount")):
                pointsGained = self.addKill(attackerUniqueID, headshot=int(ev['headshot']))
                self.tellplayer(ev["attacker"], "You killed a bot! You gained %d points." % pointsGained)
            elif attackerUniqueID == "BOT" and int(es.ServerVar("ultirank_botcount")):
                victimPointsLost = self.addDeath(victimUniqueID)
                self.tellplayer(ev["userid"], "You got killed by a bot and lost %d points." % victimPointsLost)
            else:
                attackerPointsGained = self.addKill(attackerUniqueID, headshot=int(ev['headshot']))
                victimPointsLost = self.addDeath(victimUniqueID)
                self.tellplayer(ev["attacker"], "You killed %s and gained %d points." % (ev["es_username"], attackerPointsGained))
                self.tellplayer(ev["userid"], "You got killed by %s and lost %d points." % (ev["es_attackername"], victimPointsLost))
    
rs = RankingSystem()

def createServerVar(varname, defaultvalue, description="Something", notify=False):
    """ Creates a server variable, simplified """
    sv = es.ServerVar(varname, defaultvalue, description)
    if notify:
        es.flags("add", "notify", varname)
    return sv

def load():
    createServerVar("ultirank_botcount", botKillsCounts, "Bot kills by player counts as points", True)
    createServerVar("ultirank_tk_points_decrease", tkPointsDecrease, "Tk points decrease", True)
    createServerVar("ultirank_kill_points_increase", killPointsIncrease, "Kills points increase", True)
    createServerVar("ultirank_death_points_decrease", deathPointsDecrease, "Death points decrease", True)
    createServerVar("ultirank_user_reset_per", resetRankPer, "One reset per x hours. 0 To disable.", True)
    createServerVar("ultirank_headshot_extra", headshotExtraPoints, "Headshot extra points", True)
    
    cmdlib.registerServerCommand("ultirank_upgrade", rs.upgradedb, "Upgrades the database")
    cmdlib.registerServerCommand("ultirank_enable", rs.enable, "Enable/Disales the system")
    cmdlib.registerServerCommand("ultirank_info", rs.showInfo, "Shows info about ultirank")
    
    # if the script is loaded during a round, get all users, initialize them
    for userid in es.getUseridList():
        rs.initPlayer(userid)
    
            
       
def unload():
    cmdlib.unregisterServerCommand("ultirank_upgrade")
    cmdlib.unregisterServerCommand("ultirank_enable")
    cmdlib.unregisterServerCommand("ultirank_info")
    rs.close()
 
def player_spawn(ev):
    rs.initPlayer(ev["userid"])
    
def es_map_start(ev):
    rs.checkUpdate()

def round_start(ev):
    # re-cache data
    rs.initData()
    
def player_say(ev):
    # handles the command.
    # not using say command to keep the tradition, where you can see people typing rank.
    if ev["text"].lower() == "rank":
        rs.tellPersonalRank(ev["userid"])
    elif ev["text"].lower() == "top" or ev["text"].lower() == "top10":
        rs.sendTop10Popup(ev["userid"])
    elif ev["text"].lower() == "showrank":
        rs.announcePersonalRank(ev["userid"])
    elif ev["text"].lower() == "!resetrank":
        rs.resetRank(int(ev["userid"]))
        
        
def player_death(ev):
    rs.playerDeath(ev)
        
