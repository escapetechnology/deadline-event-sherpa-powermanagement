####################################################################
## Imports
####################################################################
from Deadline.Events import *
from Deadline.Scripting import *
from System.Collections.Generic import Dictionary

VALUE_SHERPA_STARTSTOP = "Start on Startup, Stop on Idle"
VALUE_SHERPA_CREATETERMINATE = "Create on Startup, Terminate on Idle"

####################################################################
## This is the function called by Deadline to get an instance of the
## Sherpa event listener.
####################################################################
def GetDeadlineEventListener():
    return SherpaEventListener()

####################################################################
## This is the function called by Deadline when the event plugin is
## no longer in use, so that it can get cleaned up.
####################################################################
def CleanupDeadlineEventListener(deadlinePlugin):
    deadlinePlugin.Cleanup()

###############################################################
## The Sherpa event listener class.
###############################################################
class SherpaEventListener (DeadlineEventListener):
    def __init__(self):
        self.OnIdleShutdownCallback += self.OnIdleShutdown
        self.OnMachineStartupCallback += self.OnMachineStartup

    def Cleanup(self):
        del self.OnIdleShutdownCallback
        del self.OnMachineStartupCallback

    def OnMachineStartup(self, groupName, slaveNames, MachineStartupOptions):
        defaultAction = self.GetConfigEntryWithDefault("DefaultAction", VALUE_SHERPA_STARTSTOP)

        if defaultAction == VALUE_SHERPA_CREATETERMINATE:
            if defaultCreateImageID and defaultCreateSizeID:
                defaultCreateImageID = self.GetConfigEntry("DefaultCreateImageID")
                defaultCreateSizeID = self.GetConfigEntry("DefaultCreateSizeID")

                self.LogInfo("Create instance: image ID " + defaultCreateImageID + ", size ID " + defaultCreateSizeID + ".")

                # get a list of all the names of cloud regions that are defined in Deadline, for the "Sherpa" specific cloud provider
                sherpaCloudProviderRegionNames = CloudUtils.GetCloudRegionNames("Sherpa", True)

                for regionName in sherpaCloudProviderRegionNames:
                    CloudUtils.CreateInstance(
                        regionName,
                        defaultCreateSizeID,
                        defaultCreateImageID,
                        MachineStartupOptions.GetSlavesToWakeupPerInterval()
                    )
            else:
                self.LogInfo("No default create image ID and/or default create size ID specified on event plugin.")
        else:
            for slaveName in slaveNames:
                slaveSettings = RepositoryUtils.GetSlaveSettings(slaveName, True)
                instanceID = slaveSettings.GetSlaveExtraInfoKeyValue(self.GetConfigEntryWithDefault("SherpaIdentifierKey", "Sherpa_ID"))

                if instanceID:
                    self.LogInfo("Start instance: ID " + instanceID + ".")

                    # get a list of all the names of cloud regions that are defined in Deadline, for the "Sherpa" specific cloud provider
                    sherpaCloudProviderRegionNames = CloudUtils.GetCloudRegionNames("Sherpa", True)

                    for regionName in sherpaCloudProviderRegionNames:
                        CloudUtils.StartInstance(
                            regionName,
                            instanceID
                        )
                else:
                    self.LogInfo("Instance ID (" + instanceID + ") not found.")

    def OnIdleShutdown(self, groupName, slaveNames, IdleShutdownOptions):
        defaultAction = self.GetConfigEntryWithDefault("DefaultAction", VALUE_SHERPA_STARTSTOP)

        for slaveName in slaveNames:
            slaveSettings = RepositoryUtils.GetSlaveSettings(slaveName, True)
            instanceID = slaveSettings.GetSlaveExtraInfoKeyValue(self.GetConfigEntryWithDefault("SherpaIdentifierKey", "Sherpa_ID"))

            if instanceID:
                if defaultAction == VALUE_SHERPA_CREATETERMINATE:
                    self.LogInfo("Terminate instance: ID " + instanceID + ".")

                    # get a list of all the names of cloud regions that are defined in Deadline, for the "Sherpa" specific cloud provider
                    sherpaCloudProviderRegionNames = CloudUtils.GetCloudRegionNames("Sherpa", True)

                    for regionName in sherpaCloudProviderRegionNames:
                        CloudUtils.TerminateInstance(
                            regionName,
                            instanceID
                        )
                else:
                    self.LogInfo("Stop instance: ID " + instanceID + ".")

                    # get a list of all the names of cloud regions that are defined in Deadline, for the "Sherpa" specific cloud provider
                    sherpaCloudProviderRegionNames = CloudUtils.GetCloudRegionNames("Sherpa", True)

                    for regionName in sherpaCloudProviderRegionNames:
                        CloudUtils.StopInstance(
                            regionName,
                            instanceID
                        )
            else:
                self.LogInfo("Instance ID (" + instanceID + ") not found.")
