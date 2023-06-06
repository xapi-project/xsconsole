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

from XSConsoleStandard import *

class DNSDialogue(Dialogue):
    def __init__(self):
        Dialogue.__init__(self)

        data=Data.Inst()

        choiceDefs = [
            ChoiceDef(Lang("Add an DNS Server"), lambda: self.HandleInitialChoice('ADD') ) ]

        if len(data.dns.nameservers([])) > 0:
            choiceDefs.append(ChoiceDef(Lang("Remove a Single DNS Server"), lambda: self.HandleInitialChoice('REMOVE') ))
            choiceDefs.append(ChoiceDef(Lang("Remove All DNS Servers"), lambda: self.HandleInitialChoice('REMOVEALL') ))

        self.dnsMenu = Menu(self, None, Lang("Configure DNS Servers "), choiceDefs)

        self.ChangeState('INITIAL')

    def BuildPane(self):
        if self.state == 'REMOVE':
            choiceDefs = []
            for server in Data.Inst().dns.nameservers([]):
                choiceDefs.append(ChoiceDef(server, lambda: self.HandleRemoveChoice(self.removeMenu.ChoiceIndex())))

            self.removeMenu = Menu(self, None, Lang("Remove DNS Server"), choiceDefs)

        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Configure DNS Servers"))
        pane.AddBox()
        self.UpdateFields()

    def UpdateFieldsINITIAL(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please Select an Option"))
        pane.AddMenuField(self.dnsMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsADD(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please Enter the DNS Server Address"))
        pane.AddWrappedTextField(Lang("DNS nameservers."))
        pane.NewLine()
        pane.AddInputField(Lang("Server", 32), '', 'name')
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK") , Lang("<Esc>") : Lang("Cancel") } )
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)

    def UpdateFieldsREMOVE(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Select Server Entry to Remove"))
        pane.AddWrappedTextField(Lang("DNS servers."))

        pane.NewLine()

        pane.AddMenuField(self.removeMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state

    def ChangeState(self, inState):
        self.state = inState
        self.BuildPane()

    def HandleKeyINITIAL(self, inKey):
        return self.dnsMenu.HandleKey(inKey)

    def HandleKeyADD(self, inKey):
        handled = True
        pane = self.Pane()
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)
        if inKey == 'KEY_ENTER':
            inputValues = pane.GetFieldValues()
            Layout.Inst().PopDialogue()
            try:
                IPUtils.AssertValidIP(inputValues['name'])
                data=Data.Inst()
                nameservers = data.dns.nameservers([])
                nameservers.append(inputValues['name'])
                data.NameserversSet(nameservers)
                self.Commit(Lang("DNS server")+" "+inputValues['name']+" "+Lang("added"))
            except Exception, e:
                Layout.Inst().PushDialogue(InfoDialogue(Lang(e)))
        elif pane.CurrentInput().HandleKey(inKey):
            pass # Leave handled as True
        else:
            handled = False
        return handled

    def HandleKeyREMOVE(self, inKey):
        return self.removeMenu.HandleKey(inKey)

    def HandleKey(self,  inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleInitialChoice(self,  inChoice):
        data = Data.Inst()
        try:
            if inChoice == 'ADD':
                self.ChangeState('ADD')
            elif inChoice == 'REMOVE':
                self.ChangeState('REMOVE')
            elif inChoice == 'REMOVEALL':
                Layout.Inst().PopDialogue()
                data.NameserversSet([])
                self.Commit(Lang("All server entries deleted"))

        except Exception, e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Operation Failed"), Lang(e)))

        data.Update()

    def HandleRemoveChoice(self,  inChoice):
        Layout.Inst().PopDialogue()
        data=Data.Inst()
        nameservers = data.dns.nameservers([])
        thisServer = nameservers[inChoice]
        del nameservers[inChoice]
        data.NameserversSet(nameservers)
        self.Commit(Lang("DNS server")+" "+thisServer+" "+Lang("deleted"))
        data.Update()

    def Commit(self, inMessage):
        data=Data.Inst()
        try:
            data.SaveToResolveConf()
            Layout.Inst().PushDialogue(InfoDialogue( inMessage))
        except Exception, e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Update failed: ")+Lang(e)))

        data.Update()


class XSFeatureDNS:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("DNS Servers"))

        inPane.AddTitleField(Lang("Current Nameservers"))
        if len(data.dns.nameservers([])) == 0:
            inPane.AddWrappedTextField(Lang("<No nameservers are configured>"))
        for dns in data.dns.nameservers([]):
            inPane.AddWrappedTextField(str(dns))
        inPane.NewLine()
        for pif in data.derived.managementpifs([]):
            if pif['ip_configuration_mode'].lower().startswith('static'):
                inPane.AddKeyHelpField( { Lang("Enter") : Lang("Update DNS Servers") })
                break
        inPane.AddKeyHelpField( {
            Lang("<F5>") : Lang("Refresh")
        })

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'DNS', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 200,
                'menutext' : Lang('DNS Servers') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

    @classmethod
    def ActivateHandler(cls):
        data = Data.Inst()
        for pif in data.derived.managementpifs([]):
            if pif['ip_configuration_mode'].lower().startswith('static'):
                DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(DNSDialogue()))
                return

# Register this plugin when module is imported
XSFeatureDNS().Register()
