'''
Communication with the server
'''

import getpass

from twisted.internet import defer

from pdtools.coms import general
from pdtools.coms.client import RpcClient
from pdtools.lib.store import store
from pdtools.lib import riffle, names
from pdtools.lib.output import out


###############################################################################
# Riffle Implementation
###############################################################################
class ServerPerspective(riffle.RifflePerspective):

    def perspective_logs(self, logs):
        ''' New logs coming in from the server '''
        print 'New Logs!'
        for x in logs:
            print out.messageToString(x)


@defer.inlineCallbacks
def list(r):
    ''' Return the resources this user owns. '''

    avatar = yield riffle.portal.connect()
    ret = yield avatar.list()

    # I don't think this is necesary anymore, but keeping it here for now
    store.saveConfig('chutes', ret['chutes'])
    store.saveConfig('routers', ret['routers'])
    store.saveConfig('instances', ret['instances'])

    printOwned()

    defer.returnValue(ret)


# Merge this with provision!
@general.failureCallbacks
@defer.inlineCallbacks
def createRouter(r, name):
    '''
    Create a new router on the server-- do not provision it yet. 

    Like so many other things, this is a temporary method.
    '''

    avatar = yield general.connectServer()
    ret = yield avatar.provisionRouter(name)

    # Save that router's keys
    store.saveKey(ret['keys'], ret['_id'] + '.client.pem')

    ret = yield avatar.list()

    store.saveConfig('chutes', ret['chutes'])
    store.saveConfig('routers', ret['routers'])
    store.saveConfig('instances', ret['instances'])

    printOwned()

    defer.returnValue("Done")


@defer.inlineCallbacks
def logs(r, pdid):
    '''
    Query the server for all logs that the given pdid has access to. Must be a fully qualified name.

    NOTE: this method is in progress. For now, just pass the name of one of your routers.
    '''

    # Let the validation occur serverside (or skip it for now)
    pdid = store.getConfig('pdid') + '.' + pdid

    avatar = yield riffle.portal.connect()
    ret = yield avatar.logs(pdid)


###############################################################################
# Authentication Callbacks
###############################################################################


def authCallbacks(f):
    def w(*args, **kwargs):
        return f(*args, **kwargs).addCallbacks(authSuccess, general.printFailure)

    return w


def authSuccess(r):
    store.saveConfig('pdid', r['_id'])
    store.saveKey(r['keys'], 'client.pem')
    store.saveKey(r['ca'], 'ca.pem')

    print 'You have been successfully logged in.'

###############################################################################
# RPC Implementation
###############################################################################


@authCallbacks
@defer.inlineCallbacks
def login(reactor):
    name, password = None, None

    name = raw_input("Username: ")
    password = getpass.getpass()

    client = RpcClient(general.SERVER_HOST, general.SERVER_PORT, '')
    ret = yield client.login(name, password)
    defer.returnValue(ret)


@authCallbacks
@defer.inlineCallbacks
def register(reactor):
    name, email, password = raw_input("Username: "), raw_input("Email: "), getpass.getpass()

    client = RpcClient(general.SERVER_HOST, general.SERVER_PORT, '')
    ret = yield client.register(name, email, password)
    defer.returnValue(ret)

###############################################################################
# Utils
###############################################################################

# Show this individuallye (once for each type)


def printOwned():
    chutes = store.getConfig('chutes')
    routers = store.getConfig('routers')

    def pprint(d):
        print '\t' + d['_id']

    print 'routers'
    [pprint(x) for x in routers]

    print 'chutes'
    [pprint(x) for x in chutes]
