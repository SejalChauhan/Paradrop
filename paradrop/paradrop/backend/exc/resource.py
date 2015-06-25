###################################################################
# Copyright 2013-2014 All Rights Reserved
# Authors: The Paradrop Team
###################################################################
import sys

from lib.paradrop import *
from lib.paradrop.chute import Chute
from lib.paradrop import chute

from lib.internal.utils import uci
from lib.internal.utils import openwrt as osenv
from lib.internal.utils import lxc as virt
from lib.internal.exc import plangraph
from lib.internal.fc.fcerror import PDFCError
from lib.internal.fc.chutestorage import ChuteStorage

#
# Function called by the execution planner
#
def generateResourcePlan(chuteStor, newChute, chutePlan):
    """
        This function looks at a diff of the current Chute (in @chuteStor) and the @newChute, then adds Plan() calls
        to make the Chute match the @newChute.

        Returns:
            None  : means continue to pass this chute update to the rest of the chain.
            True  : means stop updating, but its ok (no errors or anything)
            str   : means stop updating, but some error occured (contained in the string)
    """
    
    new = newChute
    old = chuteStor.getChute(newChute.guid)
    out.header("-- %s Generating Resource Plan: %r\n" % (logPrefix(), new))
    
    # Check if the chute is new
    # if(not old):
    # convert cpu cgroups and add to lxcconfig (cached, key: 'cpuConfig')
    chutePlan.addPlans(new, plangraph.RESOURCE_GET_VIRT_CPU, (new.getCpuConfigString, None))
    
    # convert mem cgroups and add to lxcconfig (cached, key: 'memConfig')
    chutePlan.addPlans(new, plangraph.RESOURCE_GET_VIRT_MEM, (new.getMemConfigString, None))

    # Generate a config file for wshaper, put in cache (key: 'osResourceConfig')
    chutePlan.addPlans(new, plangraph.RESOURCE_GET_OS_CONFIG, (new.getOSResourceConfig, None))

    # Make calls to configure the wshaper UCI file
    todoPlan = (new.setOSResourceConfig, old)
    abtPlan = (new.resetOSResourceConfig, None) 
    chutePlan.addPlans(new, plangraph.RESOURCE_SET_VIRT_QOS, todoPlan, abtPlan)
    
    # Once all changes are made into UCI system, reload the wshaper daemon
    todoPlan = (osenv.reloadQos, (chuteStor, new, True)) 
    abtPlan = [(new.resetOSResourceConfig, None), (osenv.reloadQos, (chuteStor, new, False))]
    chutePlan.addPlans(new, plangraph.RESOURCE_RELOAD_QOS, todoPlan, abtPlan)

    return None
