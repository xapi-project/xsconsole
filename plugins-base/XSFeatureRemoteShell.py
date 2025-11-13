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

class DisableOptionsDialogue(Dialogue):
    SSH_MODE_DISABLE = 0
    SSH_MODE_AUTO = 2

    def __init__(self):
        Dialogue.__init__(self)

        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Auto-mode Options"))
        pane.AddBox()

        self.disableMenu = Menu(self, None, Lang("Disable Options"), [
            ChoiceDef(Lang("Always Disable"), lambda: self.HandleChoice(self.SSH_MODE_DISABLE)),
            ChoiceDef(Lang("Disable and Turn on Auto-mode"), lambda: self.HandleChoice(self.SSH_MODE_AUTO))
            ])

        self.UpdateFields()

    def UpdateFields(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("When auto-mode is enabled: SSH is disabled when XAPI is running properly, "
                        "and enabled when XAPI is down for emergency troubleshooting."))
        pane.AddMenuField(self.disableMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def HandleKey(self, inKey):
        handled = self.disableMenu.HandleKey(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleChoice(self, inChoice):
        data = Data.Inst()
        Layout.Inst().PopDialogue()

        try:
            message = Lang("Configuration Successful")
            data.DisableSSH()

            if ShellPipe(['/sbin/pidof', 'sshd-session']).CallRC() == 0: # If PIDs are available
                message = Lang("New connections via the remote shell are now disabled, but there are "
                    "ssh connections still ongoing.  If necessary, use 'killall sshd-session' from the Local "
                    "Command Shell to terminate them.")
            if inChoice == self.SSH_MODE_AUTO:
                data.SetSSHAutoMode(True)
                message = Lang("SSH auto-mode has been configured. For security,"
                        "SSH is normally disabled and will only be enabled in case of emergency.")

            Layout.Inst().PushDialogue(InfoDialogue(message))

        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue(Lang("Failed: ")+Lang(e)))

        data.Update()


class RemoteShellDialogue(Dialogue):
    SSH_MODE_ENABLE = 1

    def __init__(self):
        Dialogue.__init__(self)

        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Configure Remote Shell"))
        pane.AddBox()

        self.remoteShellMenu = Menu(self, None, Lang("Configure Remote Shell"), [
            ChoiceDef(Lang("Enable"), lambda: self.HandleChoice(self.SSH_MODE_ENABLE)),
            ChoiceDef(Lang("Disable"), lambda: self.HandleDisable())
            ])

        self.UpdateFields()

    def UpdateFields(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.AddTitleField(Lang("Please select an option"))
        pane.AddMenuField(self.remoteShellMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def HandleKey(self, inKey):
        handled = self.remoteShellMenu.HandleKey(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleChoice(self, inChoice):
        data = Data.Inst()
        Layout.Inst().PopDialogue()

        try:
            message = Lang("Configuration Successful")
            if inChoice == self.SSH_MODE_ENABLE:
                data.EnableSSH()
                Layout.Inst().PushDialogue(InfoDialogue(message))

        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue(Lang("Failed: ")+Lang(e)))

        data.Update()

    def HandleDisable(self):
        Layout.Inst().PopDialogue()
        Layout.Inst().PushDialogue(DisableOptionsDialogue())


class XSFeatureRemoteShell:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Remote Shell (ssh)"))

        if data.chkconfig.sshd() is None:
            message = Lang('unknown.  To enable or disable')
        elif data.chkconfig.sshd():
            message = Lang('enabled.  To disable')
        else:
            message = Lang('disabled.  To enable')

        inPane.AddWrappedTextField(Lang(
            "This server can accept a remote login via ssh.  Currently remote login is ") +
            message + Lang(" this feature, press <Enter>."))

        inPane.AddKeyHelpField( {
            Lang("<Enter>") : Lang("Configure Remote Shell")
        } )

    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(RemoteShellDialogue()))

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'REMOTE_SHELL', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_REMOTE',
                'menupriority' : 50,
                'menutext' : Lang('Enable/Disable/Auto Remote Shell') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureRemoteShell().Register()
