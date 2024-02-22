# Copyright (c) 2008-2009 Citrix Systems Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

if __name__ == "__main__":
    raise Exception("This script is a plugin for xsconsole and cannot run independently")

import datetime


from XSConsoleStandard import *
from XSConsoleFields import Field


class NTPDialogue(Dialogue):
    def __init__(self):
        Dialogue.__init__(self)
        self.ChangeState("INITIAL")

    def CreateINITIALPane(self):
        choiceDefs = [
            ChoiceDef(Lang("Use Default NTP Servers"), lambda: self.HandleInitialChoice('DEFAULT') ),
            ChoiceDef(Lang("Provide NTP Servers Manually"), lambda: self.HandleInitialChoice('MANUAL') ),
            ChoiceDef(Lang("Disable NTP (Manual Time Entry)"), lambda: self.HandleInitialChoice('NONE') )
        ]

        data = Data.Inst()
        pifs = data.derived.managementpifs([])
        usingDHCP = any("dhcp" in pif['ip_configuration_mode'].lower() for pif in pifs)
        if usingDHCP:
            choiceDefs.insert(0, ChoiceDef(Lang("Use DHCP NTP Servers"), lambda: self.HandleInitialChoice('DHCP')))

        if Auth.Inst().IsTestMode():
            # Show Status is a testing-only function
            choiceDefs.append(ChoiceDef(Lang("Show Status (ntpstat)"), lambda: self.HandleInitialChoice('STATUS') ))

        self.initialMenu = Menu(self, None, Lang("Configure Network Time"), choiceDefs)

    def CreateMANUALPane(self):
        choiceDefs = [
            ChoiceDef(Lang("Add New Server"), lambda: self.HandleManualChoice("ADD"))
        ]

        data = Data.Inst()
        data.UpdateFromNTPConf()

        servers = data.ntp.servers([])
        if data.ntp.method("") == "Manual" and len(servers) > 0:
            choiceDefs.append(ChoiceDef(Lang("Remove Server"), lambda: self.HandleManualChoice("REMOVE")))
            choiceDefs.append(ChoiceDef(Lang("Remove All Servers"), lambda: self.HandleManualChoice("REMOVEALL")))

        self.manualMenu = Menu(self, None, Lang("Configure Network Time"), choiceDefs)

    def ChangeState(self, state):
        self.state = state
        self.BuildPane()

    def BuildPane(self):
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Configure Network Time"))
        pane.AddBox()
        self.UpdateFields()

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, "UpdateFields" + self.state)() # Dispatch method named 'UpdateFields' + self.state

    def UpdateFieldsINITIAL(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please Select an Option"))
        self.CreateINITIALPane()
        pane.AddMenuField(self.initialMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsMANUAL(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please Select an Option"))
        self.CreateMANUALPane()
        pane.AddMenuField(self.manualMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsNONE(self):
        now = datetime.datetime.now()

        pane = self.Pane()
        pane.ResetFields()

        pane.TitleSet(Lang("Set Current Time"))
        pane.AddTitleField(Lang("Please set the current (local) date and time"))
        pane.NewLine()

        pane.AddInputField(Lang("Year: "), str(now.year), "year", inLengthLimit=4, flow=Field.FLOW_RIGHT, inputWidth=5)
        pane.AddInputField(Lang("Month: "), "{:02d}".format(now.month), "month", inLengthLimit=2, flow=Field.FLOW_RIGHT, inputWidth=5)
        pane.AddInputField(Lang("Day: "), "{:02d}".format(now.day), "day", inLengthLimit=2, inputWidth=5)
        pane.NewLine()

        pane.AddInputField(Lang("Hour (24h): "), "{:02d}".format(now.hour), "hour", inLengthLimit=2, flow=Field.FLOW_RIGHT, inputWidth=5)
        pane.AddInputField(Lang("Minute: "), "{:02d}".format(now.minute), "minute", inLengthLimit=2, inputWidth=5)

        pane.AddKeyHelpField( { Lang("<Up/Down>") : Lang("Next/Prev"), Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

        if pane.CurrentInput is None:
            pane.InputIndexSet(0)

    def UpdateFieldsADD(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please Enter the NTP Server Name(s) or Address(es)"))
        pane.NewLine()
        pane.AddInputField(Lang("Server", 16), '', 'name')

        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK") , Lang("<Esc>") : Lang("Cancel") } )
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)

    def UpdateFieldsREMOVE(self):
        pane = self.Pane()
        pane.ResetFields()

        choiceDefs = []
        for server in Data.Inst().ntp.servers([]):
            XSLog("Adding server to remove menu: " + server)
            choiceDefs.append(ChoiceDef(Lang(server), lambda: self.HandleRemoveChoice(self.removeMenu.ChoiceIndex())))

        self.removeMenu = Menu(self, None, Lang("Remove NTP Server"), choiceDefs)

        pane.AddMenuField(self.removeMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def HandleInitialChoice(self, inChoice):
        data = Data.Inst()
        try:
            if inChoice == "DHCP":
                Layout.Inst().PopDialogue()
                Layout.Inst().TransientBanner(Lang("Enabling DHCP NTP Server..."))
                data.NTPServersSet([])
                data.AddDHCPNTP()
                self.Commit(Lang("DHCP NTP Time Synchronization Enabled"))

            elif inChoice == "DEFAULT":
                Layout.Inst().PopDialogue()
                Layout.Inst().TransientBanner(Lang("Enabling Default NTP Servers..."))
                data.ResetDefaultNTPServers()
                data.RemoveDHCPNTP()
                self.Commit(Lang("Default NTP Time Synchronization Enabled"))

            elif inChoice == "MANUAL":
                self.ChangeState("MANUAL")
            elif inChoice == "NONE":
                self.ChangeState("NONE")

            elif inChoice == "STATUS":
                message = data.NTPStatus()+Lang("\n\n(Initial synchronization may take several minutes)")
                Layout.Inst().PushDialogue( Lang("NTP Status"), message))

        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Operation Failed"), Lang(e)))

        data.Update()

    def HandleManualChoice(self, inChoice):
        data = Data.Inst()
        try:
            if inChoice == "ADD":
                self.ChangeState("ADD")
            elif inChoice == "REMOVE":
                self.ChangeState("REMOVE")
            elif inChoice == "REMOVEALL":
                Layout.Inst().PopDialogue()
                Layout.Inst().TransientBanner(Lang("Removing All NTP Servers..."))
                data.NTPServersSet([])
                self.Commit(Lang("All server entries deleted"))

        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Operation Failed"), Lang(e)))

        data.Update()

    def HandleRemoveChoice(self, inChoice):
        data = Data.Inst()
        servers = data.ntp.servers([])
        thisServer = servers[inChoice]

        Layout.Inst().PopDialogue()
        Layout.Inst().TransientBanner(Lang("Removing %s NTP Server..." % thisServer))

        del servers[inChoice]
        data.NTPServersSet(servers)
        self.Commit(Lang("NTP server %s deleted" % thisServer))
        data.Update()

    def HandleKey(self, inKey): # Route any menu key presses to the current state handler
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleKeyINITIAL(self, inKey):
        return self.initialMenu.HandleKey(inKey)

    def HandleKeyMANUAL(self, inKey):
        return self.manualMenu.HandleKey(inKey)

    def HandleKeyNONE(self, inKey):
        handled = True
        pane = self.Pane()
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)

        if inKey == 'KEY_ENTER':
            inputValues = pane.GetFieldValues()
            Layout.Inst().PopDialogue()

            try:
                year = inputValues["year"].strip()
                month = inputValues["month"].strip()
                day = inputValues["day"].strip()
                hour = inputValues["hour"].strip()
                minute = inputValues["minute"].strip()

                date_string = "%04d-%02d-%02d %02d:%02d:00" % (int(year), int(month), int(day), int(hour), int(minute))
                date_format = "%Y-%m-%d %H:%M:00"
                date = datetime.datetime.strptime(date_string, date_format)

                Layout.Inst().TransientBanner(Lang("Setting Time..."))
                data = Data.Inst()
                data.RemoveDHCPNTP()
                data.SetTimeManually(date)

                self.Commit(Lang("Time Set Manually"), restartChronyd=False)
            except Exception as e:
                Layout.Inst().PushDialogue(InfoDialogue(Lang(e)))

        elif inKey == 'KEY_DOWN':
            newIndex = (pane.InputIndex() + 1) % pane.fieldGroup.NumInputFields()
            pane.InputIndexSet(newIndex)
        elif inKey == 'KEY_UP':
            newIndex = (pane.InputIndex() - 1) % pane.fieldGroup.NumInputFields()
            pane.InputIndexSet(newIndex)

        elif pane.CurrentInput().HandleKey(inKey):
            pass
        else:
            handled = False

        return handled

    def HandleKeyADD(self, inKey):
        handled = True
        pane = self.Pane()
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)
        if inKey == 'KEY_ENTER':
            inputValues = pane.GetFieldValues()
            Layout.Inst().PopDialogue()
            Layout.Inst().TransientBanner(Lang("Adding %s NTP Server..." % inputValues['name']))
            try:
                IPUtils.AssertValidNetworkName(inputValues['name'])

                data=Data.Inst()
                if data.ntp.method("") == "Default":
                    data.NTPServersSet([server for server in data.ntp.servers([]) if "centos.pool.ntp.org" not in server])

                data.RemoveDHCPNTP()

                servers = data.ntp.servers([])
                servers.append(inputValues['name'])
                data.NTPServersSet(servers)
                self.Commit(Lang("NTP server")+" "+inputValues['name']+" "+Lang("added"))
            except Exception as e:
                Layout.Inst().PushDialogue(InfoDialogue(Lang(e)))

        elif pane.CurrentInput().HandleKey(inKey):
            pass # Leave handled as True
        else:
            handled = False
        return handled

    def HandleKeyREMOVE(self, inKey):
        return self.removeMenu.HandleKey(inKey)

    def Commit(self, inMessage, restartChronyd=True):
        data=Data.Inst()
        try:
            data.SaveToNTPConf()
            if restartChronyd:
                Layout.Inst().TransientBanner(Lang("Restarting NTP daemon with new configuration..."))
                data.RestartService('chronyd')
            Layout.Inst().PushDialogue(InfoDialogue( inMessage))
        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Update failed: ")+Lang(e)))

        data.Update()


class XSFeatureNTP:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        data.UpdateFromNTPConf()

        inPane.AddTitleField(Lang("Network Time (NTP)"))

        inPane.AddWrappedTextField(Lang("One or more network time servers can be configured to synchronize time between servers.  This is especially important for pooled servers."))
        inPane.NewLine()

        ntpMethod = data.ntp.method("<Unknown>")
        if ntpMethod == "Disabled":
            inPane.AddWrappedTextField(Lang("Currently NTP is disabled."))
        else:
            inPane.AddWrappedTextField(Lang("Currently NTP is enabled, and the following servers are configured."))

            servers = data.ntp.servers([])
            if ntpMethod == "DHCP":
                gateway = data.ManagementGateway()
                if gateway is None:
                    gateway = "Refreshing..."

                servers = [Lang(str(gateway) + " (DHCP)")]

            inPane.NewLine()

            if len(servers) == 0:
                inPane.AddWrappedTextField(Lang("<No servers configured>"))
            else:
                for server in servers:
                    inPane.AddWrappedTextField(server)

        inPane.AddKeyHelpField( {
            Lang("<Enter>") : Lang("Reconfigure"),
            Lang("<F5>") : Lang("Refresh")
        })

    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(NTPDialogue()))

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'NTP', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 300,
                'menutext' : Lang('Network Time (NTP)') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureNTP().Register()
