####################################################################
## Imports
####################################################################
from Deadline.Events import *
from Deadline.Scripting import *
from System.Collections.Generic import Dictionary

ACTION_START = "start"
ACTION_STOP = "stop"

####################################################################
## This is the function called by Deadline to get an instance of the
## Sherpa power management event listener.
####################################################################
def GetDeadlineEventListener():
    return SherpaPowerManagementEventListener()

####################################################################
## This is the function called by Deadline when the event plugin is
## no longer in use, so that it can get cleaned up.
####################################################################
def CleanupDeadlineEventListener(deadlinePlugin):
    deadlinePlugin.Cleanup()

###############################################################
## The Sherpa power management event listener class.
###############################################################
class SherpaPowerManagementEventListener(DeadlineEventListener):
    def __init__(self):
        self.OnIdleShutdownCallback += self.OnIdleShutdown
        self.OnMachineStartupCallback += self.OnMachineStartup

    def Cleanup(self):
        del self.OnIdleShutdownCallback
        del self.OnMachineStartupCallback

    def OnMachineStartup(self, groupName, slaveNames, MachineStartupOptions):
        self.__handle(ACTION_START, slaveNames)

    def OnIdleShutdown(self, groupName, slaveNames, IdleShutdownOptions):
        self.__handle(ACTION_STOP, slaveNames)

    def __handle(self, action, slaveNames):
        for slaveName in slaveNames:
            slaveSettings = RepositoryUtils.GetSlaveSettings(slaveName, True)
            instanceID = slaveSettings.GetSlaveExtraInfoKeyValue(self.GetConfigEntryWithDefault("SherpaIdentifierKey", "Sherpa_ID"))

            if instanceID:
                self.LogInfo(action.capitalize() + " instance: ID " + instanceID + ".")

                # get a list of all the names of cloud regions that are defined in Deadline, for the "Sherpa" specific cloud provider
                sherpaCloudProviderRegionNames = CloudUtils.GetCloudRegionNames("Sherpa", True)

                for regionName in sherpaCloudProviderRegionNames:
                    if action == ACTION_START:
                        CloudUtils.StartInstance(
                            regionName,
                            instanceID
                        )
                    else:
                        CloudUtils.StopInstance(
                            regionName,
                            instanceID
                        )
            else:
                self.LogInfo("Instance ID (" + instanceID + ") not found.")
