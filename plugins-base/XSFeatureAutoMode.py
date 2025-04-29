# Copyright (c) Cloud Software Group, Inc.
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

class AutoModeDialogue(Dialogue):
    def __init__(self):
        Dialogue.__init__(self)
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Configure SSH Auto Mode"))
        pane.AddBox()

        self.autoModeMenu = Menu(self, None, Lang("Configure SSH Auto Mode"), [
            ChoiceDef(Lang("Enable Auto Mode"), lambda: self.HandleChoice(True)),
            ChoiceDef(Lang("Disable Auto Mode"), lambda: self.HandleChoice(False))
            ])

        self.UpdateFields()

    def UpdateFields(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please select an option"))
        pane.AddMenuField(self.autoModeMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def HandleKey(self, inKey):
        handled = self.autoModeMenu.HandleKey(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleChoice(self, inChoice):
        data = Data.Inst()
        Layout.Inst().PopDialogue()

        try:
            if inChoice:
                data.SetSSHAutoMode(True)
                message = Lang("SSH Auto Mode Enabled")
            else:
                data.SetSSHAutoMode(False)
                message = Lang("SSH Auto Mode Disabled")

            Layout.Inst().PushDialogue(InfoDialogue(message))

        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue(Lang("Failed: ")+Lang(e)))

        data.Update()


class XSFeatureAutoMode:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("SSH Auto Mode"))

        try:
            autoModeStatus = False
            if Auth.Inst().IsAuthenticated():
                autoModeStatus = data.GetSSHAutoMode()
            
            if autoModeStatus:
                message = Lang('enabled. To disable')
            else:
                message = Lang('disabled. To enable')

            inPane.AddWrappedTextField(Lang(
                "SSH Auto Mode allows the system to automatically enable or disable SSH based on XAPI conditions. "
                "Currently SSH Auto Mode is ") + message + Lang(" this feature, press <Enter>."))
        except Exception as e:
            inPane.AddWrappedTextField(Lang(
                "SSH Auto Mode information is not available. Please log in to access this feature."))

        inPane.AddKeyHelpField( {
            Lang("<Enter>") : Lang("Configure SSH Auto Mode")
        } )

    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(AutoModeDialogue()))

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'SSH_AUTO_MODE', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_REMOTE',
                'menupriority' : 110,
                'menutext' : Lang('Configure SSH Auto Mode'),
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureAutoMode().Register() 
