###################################################################
# Copyright 2013-2014 All Rights Reserved
# Authors: The Paradrop Team
###################################################################

import sys, json, copy, base64

from paradrop.lib.utils.output import out, logPrefix
from paradrop.lib.utils.pdutils import timeint, str2json
from paradrop.lib.utils import pdos
from paradrop.lib import settings

from paradrop.lib.utils.storage import PDStorage

from paradrop.lib.chute import Chute

class ChuteStorage(PDStorage):
    """
        ChuteStorage class.

        This class holds onto the list of Chutes on this AP.
        
        It implements the PDStorage class which allows us to save the chuteList to disk transparently
    """
    # Class variable of chute list so all instances see the same thing
    chuteList = dict()
    
    def __init__(self, filename=None, reactor=None):
        if(not filename):
            filename = settings.FC_CHUTESTORAGE_SAVE_PATH
        PDStorage.__init__(self, filename, "chuteList", reactor, settings.FC_CHUTESTORAGE_SAVE_TIMER)

        # Has it been loaded?
        if(len(ChuteStorage.chuteList) == 0):
            out.verbose('   %s Loading chutes from disk: %s\n' % (logPrefix(), filename))
            self.loadFromDisk()

    def getChuteList(self):
        """Return a list of the GUIDs of the chutes we know of."""
        return list(ChuteStorage.chuteList.values())

    def getChute(self, name):
        """Returns a reference to a chute we have in our cache, or None."""
        return ChuteStorage.chuteList.get(name, None)
  
    def deleteChute(self, ch):
        """Deletes a chute from the chute storage. Can be sent the chute object, or the chute name."""
        if (isinstance(ch, Chute)):
            del ChuteStorage.chuteList[ch.name]
        else:
            del ChuteStorage.chuteList[ch]
        self.saveToDisk()
         
    def saveChute(self, ch):
        """
            Saves the chute provided in our internal chuteList.
            Also since we just received a new chute to hold onto we should save our ChuteList to disk.
        """
        # check if there is a version of the chute already
        oldch = ChuteStorage.chuteList.get(ch.name, None)
        if(oldch):
            newch = copy.deepcopy(oldch)
            # we should merge these chutes so we don't lose any data
            # First set the regular data
            for k,v in ch.getAPIDataFormat().iteritems():
                setattr(newch, k, v)
            # Now deal with cache separately
            for k,v in ch._cache.iteritems():
                newch._cache[k] = v
            # this allows us to keep what WAS there, replace any duplicates with new stuff without loosing anything too
            ChuteStorage.chuteList[ch.name] = newch
        else:
            ChuteStorage.chuteList[ch.name] = ch
        self.saveToDisk()
    
    def clearChuteStorage(self):
        ChuteStorage.chuteList = {}
        pdos.remove(settings.FC_CHUTESTORAGE_SAVE_PATH)
    
    #
    # Functions we override to implement PDStorage Properly
    #
    def attrSaveable(self):
        """Returns True if we should save the ChuteList, otherwise False."""
        return (type(ChuteStorage.chuteList) == dict)

    def importAttr(self, pyld):
        """Takes an array of dicts that represent Chutes and converts them into a list of Chute objects.
            Raises Exception if name missing from Chute.
            Returns dict[name] = Chute
            """
        pyld = json.loads(base64.b64decode(pyld), object_hook=convertUnicode)
        d = {}
        for p in pyld:
            c = Chute(p)
            if(c.name == ""):
                raise Exception('importChuteList', 'Missing name from Chute object')
            d[c.name] = c

        #print("importChuteList\n%s" % d)
        return d
    
    def exportAttr(self, cl):
        """Takes a chutelist (dict of Chute objects) and returns a string representing an array of chutes in API Data format."""
        return base64.b64encode(json.dumps([c.fullDump() for c in ChuteStorage.chuteList.values()]))

if(__name__ == '__main__'):
    def usage():
        print('Usage: $0 -ls : print chute storage details')
        exit(0)
        
    try:
        if(sys.argv[1] != '-ls'):
            usage()
    except Exception as e:
        print(e)
        usage()
        
    cs = ChuteStorage()

    chutes = cs.getChuteList()
    for ch in chutes:
        print(ch)