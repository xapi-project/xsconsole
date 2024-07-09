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
import subprocess

def _listBackups(sr_uuid, vdi_uuid, legacy=False):
    # list the available backups
    Layout.Inst().TransientBanner(Lang("Found VDI, retrieving available backups..."))
    command = ["%s/xe-restore-metadata" % (Config.Inst().HelperPath(),), "-l", "-u", sr_uuid, "-x", vdi_uuid]
    if legacy:
        command.append("-o")
    cmd = subprocess.Popen(command,
                           stdout = subprocess.PIPE,
                           stderr = subprocess.PIPE,
                           universal_newlines = True)
    output, errput = cmd.communicate()
    status = cmd.returncode
    if status != 0:
        raise Exception("(%s,%s)" % (output,errput))
    Layout.Inst().PushDialogue(DRRestoreSelection(output, vdi_uuid, sr_uuid, legacy=legacy))

class DRRestoreVDISelection(Dialogue):
    def __init__(self, sr_uuid, vdi_uuids):
        Dialogue.__init__(self)

        choices = []

        self.sr_uuid = sr_uuid
        self.vdi_uuids = vdi_uuids
        index = 0
        for choice in self.vdi_uuids:
            cdef = ChoiceDef(choice, lambda i=index: self.HandleVDIChoice(i))
            index = index + 1
            choices.append(cdef)

        self.testMenu = Menu(self, None, "", choices)
        self.ChangeState('LISTVDIS')

    def BuildPane(self):
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang('Restore Virtual Machine Metadata'))
        pane.AddBox()

    def UpdateFieldsLISTVDIS(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.TitleSet("Available Metadata VDIs")
        pane.AddTitleField(Lang("Select Metadata VDI to Restore From"))
        pane.AddWarningField(Lang("You should only restore metadata from a trustworthy VDI; loading untrustworthy metadata may put your system at risk"))
        pane.AddMenuField(self.testMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state

    def ChangeState(self, inState):
        self.state = inState
        self.BuildPane()
        self.UpdateFields()

    def HandleVDIChoice(self, inChoice):
        _listBackups(self.sr_uuid, self.vdi_uuids[inChoice], legacy=True)

    def HandleKeyLISTVDIS(self, inKey):
        handled = self.testMenu.HandleKey(inKey)
        if not handled and inKey == 'KEY_LEFT':
            Layout.Inst().PopDialogue()
            handled = True
        return handled

    def HandleKey(self, inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

class DRRestoreSelection(Dialogue):

    def __init__(self, date_choices, vdi_uuid, sr_uuid, legacy=False):
        Dialogue.__init__(self)

        choices = []
        self.vdi_uuid = vdi_uuid
        self.sr_uuid = sr_uuid
        self.legacy = legacy
        self.date_choices = date_choices.splitlines()
        index = 0
        for choice in self.date_choices:
            cdef = ChoiceDef(choice, lambda i=index: self.HandleTestChoice(i))
            index = index + 1
            choices.append(cdef)

        self.testMenu = Menu(self, None, "", choices)

        self.methodMenu = Menu(self, None, "", [
           ChoiceDef("Only VMs on This SR", lambda: self.HandleMethodChoice('sr', False)),
           ChoiceDef("All VM Metadata", lambda: self.HandleMethodChoice('all', False)),
           ChoiceDef("Only VMs on This SR (Dry Run)", lambda: self.HandleMethodChoice('sr', True)),
           ChoiceDef("All VM Metadata (Dry Run)", lambda: self.HandleMethodChoice('all', True)),
        ])
        self.ChangeState('LISTDATES')

    def BuildPane(self):
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang('Restore Virtual Machine Metadata'))
        pane.AddBox()

    def UpdateFieldsLISTDATES(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.TitleSet("Available Metadata Backups")
        pane.AddTitleField(Lang("Select Metadata Backup to Restore From"))
        pane.AddMenuField(self.testMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsCHOOSERESTORE(self):
        pane = self.Pane()
        pane.ResetFields()

        pane.TitleSet("Restore Backup from " + self.chosen_date)
        pane.AddTitleField("Select the set of VMs to restore from " + self.chosen_date)
        pane.AddMenuField(self.methodMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("Restore VMs"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state

    def ChangeState(self, inState):
        self.state = inState
        self.BuildPane()
        self.UpdateFields()

    def HandleTestChoice(self,  inChoice):
        self.chosen_date = self.date_choices[inChoice]
        self.ChangeState('CHOOSERESTORE')

    def HandleMethodChoice(self, inChoice, dryRun):
        if inChoice != 'sr' and inChoice != 'all':
            Layout.Inst().PopDialogue()
            Layout.Inst().PushDialogue(InfoDialogue(Lang("Internal Error, unexpected choice: " + inChoice)))
        else:
            chosen_mode = inChoice
            Layout.Inst().TransientBanner(Lang("Restoring VM Metadata.  This may take a few minutes..."))
            command = ["%s/xe-restore-metadata" % (Config.Inst().HelperPath(),), "-y", "-u", self.sr_uuid, "-x", self.vdi_uuid, "-d", self.chosen_date, "-m", chosen_mode]
            if dryRun:
                command.append("-n")
            if self.legacy:
                command.append("-o")

            cmd = subprocess.Popen(command,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.STDOUT,
                                universal_newlines = True)
            output, _ = cmd.communicate()
            status = cmd.returncode
            Layout.Inst().PopDialogue()
            if status == 0:
                Layout.Inst().PushDialogue(InfoDialogue(Lang("Metadata Restore Succeeded: ") + output))
            else:
                XSLogFailure('Metadata restore failed: '+str(output))
                Layout.Inst().PushDialogue(InfoDialogue(Lang("Metadata Restore Failed: ") + output))

    def HandleKey(self, inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleKeyLISTDATES(self, inKey):
        handled = self.testMenu.HandleKey(inKey)
        if not handled and inKey == 'KEY_LEFT':
            Layout.Inst().PopDialogue()
            handled = True
        return handled

    def HandleKeyCHOOSERESTORE(self, inKey):
        handled = self.methodMenu.HandleKey(inKey)
        if not handled and inKey == 'KEY_LEFT':
            Layout.Inst().PopDialogue()
            handled = True
        return handled

class DRRestoreDialogue(SRDialogue):
    def __init__(self):

        self.custom = {
            'title' : Lang("Select Storage Repository to Restore From"),
            'prompt' : Lang("Please select a Storage Repository"),
            'mode' : 'rw',
            'capabilities' : 'vdi_create'
        }
        SRDialogue.__init__(self) # Must fill in self.custom before calling __init__

    def _searchForVDI(self, sr_uuid, legacy=False):
        # probe for the restore VDI UUID
        command = ["%s/xe-restore-metadata" % (Config.Inst().HelperPath(),), "-p", "-u", sr_uuid]
        if legacy:
            command.append("-o")
        cmd = subprocess.Popen(command,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               universal_newlines = True)
        output, errput = cmd.communicate()
        status = cmd.returncode
        if status != 0:
            raise Exception("(%s,%s)" % (output,errput))
        if len(output) == 0:
            raise Exception(errput)
        return output

    def _earlierConfirmHandler(self, inYesNo, sr_uuid):
        if inYesNo == 'y':
            Layout.Inst().TransientBanner(Lang("Searching for backup VDI...\n\nCtrl-C to abort"))
            try:
                vdi_uuids = [v.strip() for v in self._searchForVDI(sr_uuid, legacy=True).splitlines()]
                if len(vdi_uuids) == 1:
                    _listBackups(sr_uuid, vdi_uuids[0], legacy=True)
                else:
                    Layout.Inst().PushDialogue(DRRestoreVDISelection(sr_uuid, vdi_uuids))
                    return
            except Exception as e:
                Layout.Inst().PushDialogue(InfoDialogue( Lang("Metadata Restore failed: ")+Lang(e)))
        else:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Metadata Restore failed: a backup VDI could not be found")))
        Data.Inst().Update()

    def DoAction(self, inSR):
        Layout.Inst().PopDialogue()
        Layout.Inst().TransientBanner(Lang("Searching for backup VDI...\n\nCtrl-C to abort"))
        sr_uuid = inSR['uuid']
        try:
            try:
                vdi_uuid = self._searchForVDI(sr_uuid).strip()
            except Exception as e:
                # We could not uniquely identify the required VDI, ask the user if they want to check for legacy ones
                message = Lang("A backup VDI could not be positively identified. Do you wish to scan for backup VDIs created with earlier versions (Warning: this operation should only be performed if you trust the contents of all VDIs in this storage repository)?")
                Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: self._earlierConfirmHandler(x, sr_uuid)))
                return

            _listBackups(sr_uuid, vdi_uuid)
        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Metadata Restore failed: ")+Lang(e)))
        Data.Inst().Update()

class XSFeatureDRRestore:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Restore Virtual Machine Metadata"))

        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to restore Virtual Machine metadata from a Storage Repository."))
        inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Backup") } )

    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(DRRestoreDialogue()))

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'DRRESTORE', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_BUR',
                'menupriority' : 90,
                'menutext' : Lang('Restore Virtual Machine Metadata') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureDRRestore().Register()
