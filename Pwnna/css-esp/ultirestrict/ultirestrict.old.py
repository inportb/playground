import es
# Config #
restricted = "awp;g3sg1;sg550"
# Config Ends Here #


info = es.AddonInfo()
info.name         = "UltiRestrict"
info.version      = "0.1-beta"
info.author       = "Ulti"
info.description  = "Restrict weapons"
info.url          = "http://addons.eventscripts.com/addons/view/ultirestrict"
info.basename     = "ultirestrict"

restrictedList = []

def load():
    getWeapon()
    if es.exists("command", "ur_clear") == 0:
        es.regcmd("ur_clear", "ultirestrict/clearwep", "Clears the restricted list.")

    if es.exists("command", "ur_add") == 0:
        es.regcmd("ur_add", "ultirestrict/addwep", "Add a restricted weapon.")

    if es.exists("command", "ur_del") == 0:
        es.regcmd("ur_del", "ultirestrict/delwep", "Remove a restricted weapon.")

    #if es.exists("command", "ur_knivesonly") == 0:
    #    es.regcmd("ur_knivesonly", "ultirestrict/knives", "Set knives only.")

    weplist = ", ".join(restrictedList)
    es.addons.registerClientCommandFilter(restrict)

def unload():
    es.addons.unregisterClientCommandFilter(restrict)

def getWeapon():
    global restrictedList
    delimiter = ";"
    if restricted == "":
        restrictedList = []
    else:
        restrictedList = restricted.split(delimiter)

def clearwep():
    global restrictedList
    restrictedList = []
    es.server.queuecmd("echo [UltiRestrict] Restricted Weapon List Cleared! The List is now " + str(restrictedList))

def addwep():
    global restrictedList
    argument = es.getargv(1)
    if argument not in restrictedList:
        restrictedList.append(argument)
    es.server.queuecmd("echo [UltiRestrict] The new list is now: " + str(restrictedList))
    
def delwep():
    global restrictedList
    argument = es.getargv(1)
    if argument in restrictedList:
        restrictedList.remove(argument)
        es.server.queuecmd("echo [UltiRestrict] The new list is now: " + str(restrictedList))
    else:
        es.server.queuecmd("echo [UltiRestrict] The weapon you requested is not in the list.")

def knives():
    global restrictedList
    restrictedList = ["glock","usp","p228","deagle","elite","fiveseven","m3","xm1014","mac10","tmp","mp5navy","ump45","p90","galil","famas","ak47","m4a1","scout","sg550","aug","awp","g3sg1","sg552","m249"]
    userList = es.getUseridList()
    es.cexec_all("drop")
    
def restrict(userid, args):
    if args[0].lower() == "buy":
        attemptBuy = args[1].lower()
        if attemptBuy in restrictedList:
            es.tell(userid, "#multi","#green[UltiRestrict] #default%s is restricted!" % attemptBuy)
            return False
    return True

def item_pickup(event_var):
    pickingup = event_var["item"]
    if str(pickingup) in restrictedList:
        weapon = "weapon_%s" % pickingup
        es.sexec(event_var["userid"], "drop")
        es.server.queuecmd("es_xremove %s" % weapon)
        es.tell(event_var["userid"], "#multi", "#green[UltiRestrict] #default%s is restricted!" % pickingup)

def round_start(event_var):
    weplist = ", ".join(restrictedList)
    es.msg("#multi","#green[UltiRestrict] #defaultThe currect restricted weapon list is:", weplist)
