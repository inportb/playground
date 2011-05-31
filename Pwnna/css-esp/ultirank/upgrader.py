# +-----------------------------------------------+
# | UltiRank DB Uprader                           |
# | filename: upgrader.py                         |
# | Created by Ulti - http://thekks.net           |
# | Status: Beta                                  |
# | Website: http://thekks.net                    |
# | Requirement: EventScript 2.1 or higher        |
# +-----------------------------------------------+
# |                    Credits                    |
# | Design: KKSNetwork                            |
# | Coding: Ultimatebuster                        |
# +-----------------------------------------------+

# should be pyc when published so no one can mess with it.

from_version = (0.1, )
to_version = 0.2

import shelve, shutil

GENERAL_FAILURE = -1
SUCCESS = 0
FROM_VERSION_MISMATCH = 1
TO_VERSION_MISMATCH = 2
DB_ALREADY_UPTODATE = 3

def upgrade(toversion, path):    
    # Check to version
    if toversion != to_version:
        return TO_VERSION_MISMATCH
    
    # Open database
    db = shelve.open(path, writeback=True)
    
    # Make back up
    shutil.copy(path, path + (".%.2f.bak" % db['version']))
    
    # Check from version
    if db["version"] not in from_version:
        db.close()
        return FROM_VERSION_MISMATCH
    
    # Check if it's already up to date
    if db["version"] == to_version:
        db.close()
        return DB_ALREADY_UPTODATE
    
    
    # perform upgrade
    returnCode = _performupgrade(db)

    if returnCode == SUCCESS:
        db["version"] = to_version
        db.close()
        return SUCCESS
    else:
        return returnCode

def _performupgrade(db):
    for uniqueid in db:
        if uniqueid == "method" or uniqueid == "version":
            continue
        db[uniqueid]["resettime"] = 0.0
    return SUCCESS
    
