# Copyright (c) 2025 Cloud Software Group, Inc.
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

class DMVUtils:
    @classmethod
    def DriverVariantChoiceName(cls, variant, prefix = None):
        variantName = variant['name']
        variantVersion = variant['version']
        variantText = ""
        if prefix is None:
            variantText = "%s (%s)" % (variantName, variantVersion)
        else:
            variantText = "%s %s (%s)" % (prefix, variantName, variantVersion)
        return variantText

    @classmethod
    def ActiveDriverVariantChoiceName(cls, variant):
        return cls.DriverVariantChoiceName(variant, "[A]")

    @classmethod
    def SelectedDriverVariantChoiceName(cls, variant):
        return cls.DriverVariantChoiceName(variant, "[S]")

    @classmethod
    def RunningDriverVariantChoiceName(cls, variant):
        return cls.DriverVariantChoiceName(variant, "[*]")

    @classmethod
    def CandidateDriverVariantChoiceName(cls, variant):
        return cls.DriverVariantChoiceName(variant, "[ ]")

    @classmethod
    def GetVariantRecord(cls, variantOpaqueRef):
        variant = Task.Sync(lambda x: x.xenapi.Driver_variant.get_record(variantOpaqueRef))
        return variant

    @classmethod
    def GetSelectedDriverVariantUUID(cls, driver):
        variantRef = driver.selected_variant(None)
        if variantRef is None:
            return None
        variant = Task.Sync(lambda x: x.xenapi.Driver_variant.get_record(variantRef.OpaqueRef()))
        return variant['uuid']

    @classmethod
    def DoSelect(cls, inDMVHandle, variantRef):
        driver = HotAccessor().dmv[inDMVHandle]
        driverRef = driver.HotOpaqueRef().OpaqueRef()

        # This is an immediate operation, cannot be executed in async mode.
        Task.Sync(lambda x: x.xenapi.Host_driver.select(driverRef, variantRef))

class DriverSelectDialogue(Dialogue):
    def __init__(self, inDMVHandle):
        self.dmvHandle = inDMVHandle
        Dialogue.__init__(self)

        driver = HotAccessor().dmv[self.dmvHandle]
        driverRef = driver.HotOpaqueRef().OpaqueRef()
        variants = Task.Sync(lambda x: x.xenapi.Driver_variant.get_all_records_where('field "driver" = "%s"' % driverRef))

        activeList = []
        activeVariantRef = driver.active_variant(None)
        if activeVariantRef:
            activeList.append(activeVariantRef.OpaqueRef())

        selectedList = []
        selectedVariantRef = driver.selected_variant(None)
        if selectedVariantRef:
            selectedList.append(selectedVariantRef.OpaqueRef())

        self.selectMenu = Menu()
        for variantRef in variants:
            isActive = False
            isSelected = False

            record = variants[variantRef]
            choiceName = DMVUtils.DriverVariantChoiceName(record)
            if variantRef in activeList:
                isActive = True
            if variantRef in selectedList:
                isSelected = True

            if isActive and isSelected:
                choiceName = DMVUtils.RunningDriverVariantChoiceName(record)
            elif isActive:
                choiceName = DMVUtils.ActiveDriverVariantChoiceName(record)
            elif isSelected:
                choiceName = DMVUtils.SelectedDriverVariantChoiceName(record)
            else:
                choiceName = DMVUtils.CandidateDriverVariantChoiceName(record)

            self.selectMenu.AddChoice(name = choiceName,
                onAction = self.HandleControlChoice,
                handle = variantRef)
        if self.selectMenu.NumChoices() == 0:
            self.selectMenu.AddChoice(name = Lang('<No Driver Variant Available>'))

        self.ChangeState('INITIAL')

    def BuildPane(self):
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang('Select Driver'))
        pane.AddBox()

    def UpdateFieldsINITIAL(self):
        pane = self.Pane()
        pane.ResetFields()

        driver = HotAccessor().dmv[self.dmvHandle]
        driverName = convert_anything_to_str(driver.friendly_name(None))
        if driverName is None:
            pane.AddTitleField(Lang("The Multi Version Driver is no longer present"))
        else:
            pane.AddTitleField(Lang("Select variant for driver ")+driverName+' (A active, S selected, * active + selected).')

        pane.AddMenuField(self.selectMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsCONFIRM(self):
        pane = self.Pane()
        pane.ResetFields()

        variant = self.selectedVariant

        driver = HotAccessor().dmv[self.dmvHandle]
        driverName = convert_anything_to_str(driver.friendly_name(None))
        if driverName is None:
            pane.AddTitleField(Lang("The Multi Version Driver is no longer present"))
        else:
            pane.AddTitleField(Lang('Press <F8> to confirm this selection'))
            pane.AddStatusField(Lang("Driver", 20), driverName)
            pane.AddStatusField(Lang("Variant", 20), variant['name'])

        pane.AddKeyHelpField( { Lang("<F8>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state

    def ChangeState(self, inState):
        self.state = inState
        self.BuildPane()
        self.UpdateFields()

    def HandleKeyINITIAL(self, inKey):
        return self.selectMenu.HandleKey(inKey)

    def HandleKeyCONFIRM(self, inKey):
        handled = False
        if inKey == 'KEY_F(8)':
            self.Commit()
            handled = True
        return handled

    def HandleKey(self,  inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)

        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled

    def HandleControlChoice(self, inChoice):
        self.selectedVariantOpaqueRef = inChoice
        self.selectedVariant = DMVUtils.GetVariantRecord(self.selectedVariantOpaqueRef)
        self.ChangeState('CONFIRM')

    def Commit(self):
        Layout.Inst().PopDialogue()

        variant = self.selectedVariant
        variantName = variant['name']
        variantUUID = variant['uuid']
        driver = HotAccessor().dmv[self.dmvHandle]
        driverName = convert_anything_to_str(driver.friendly_name(None))

        # Just return if the new selection equals to the old one.
        oldSelectedVarUUID = DMVUtils.GetSelectedDriverVariantUUID(driver)
        if oldSelectedVarUUID == variantUUID:
            message = Lang('No selecting variant ') + variantName + Lang(' for driver ') + driverName + Lang(' again.')
            Layout.Inst().PushDialogue(InfoDialogue(message))
            return

        messagePrefix = Lang('Selecting variant ') + variantName + Lang(' for driver ') + driverName + Lang(' ')
        try:
            DMVUtils.DoSelect(self.dmvHandle, self.selectedVariantOpaqueRef)

            promptMessage = Lang('successful.\n\nPlease reboot host to enable the selected variant.')
            Layout.Inst().PushDialogue(InfoDialogue(messagePrefix + promptMessage))
        except Exception as e:
            Layout.Inst().PushDialogue(InfoDialogue(messagePrefix + Lang("Failed."), Lang(e)))

class XSFeatureDMV:
    @classmethod
    def PresentStatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Driver Variants Information"))

        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to display detailed information about hardware present driver variants on this host."))

    @classmethod
    def AllStatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Driver Variants Information"))

        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to display detailed information about all driver variants on this host."))

    @classmethod
    def NoDMVStatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Driver Variants Information"))

        inPane.AddWrappedTextField(Lang("There are no Multi Version Drivers on this host."))

    @classmethod
    def InfoStatusUpdateHandler(cls, inPane, inHandle):
        driver = HotAccessor().dmv[inHandle]
        if driver is None:
            inPane.AddWrappedTextField(Lang("This Multi Version Driver is no longer present"))
        else:
            driverType = driver.type(Lang('<Unknown>'))
            driverDesc = driver.description(Lang('<Unknown>'))
            driverInfo = driver.info(Lang('<Unknown>'))

            inPane.AddWrappedTextField(driver.friendly_name(Lang('<Unknown>')))
            inPane.NewLine()
            inPane.AddStatusField(Lang("Device Type", 16), driverType)
            inPane.AddStatusField(Lang("Description", 16), driverDesc)
            inPane.AddStatusField(Lang("Info", 16), driverInfo)

            driverRef = driver.HotOpaqueRef().OpaqueRef()
            activeVarRef = driver.active_variant(None).OpaqueRef()
            selectedVarRef = driver.selected_variant(None).OpaqueRef()
            variants = Task.Sync(lambda x: x.xenapi.Driver_variant.get_all_records_where('field "driver" = "%s"' % driverRef))
            if len(variants) > 0:
                variantList = []
                hw_present = False
                activeVariant = None
                selectedVariant = None

                for variantRef in variants:
                    record = variants[variantRef]
                    variantList.append(DMVUtils.DriverVariantChoiceName(record))
                    if record['hardware_present']:
                        hw_present = True
                    if selectedVarRef == variantRef:
                        selectedVariant = record
                    if activeVarRef == variantRef:
                        activeVariant = record

                if hw_present:
                    inPane.AddStatusField(Lang("Device Present", 16), "Yes")

                    inPane.NewLine()
                    inPane.AddWrappedBoldTextField(Lang('Active Variant'))
                    if activeVariant:
                        text = DMVUtils.DriverVariantChoiceName(activeVariant)
                        inPane.AddWrappedTextField(text)
                    else:
                        inPane.AddWrappedTextField(Lang('No'))

                    inPane.NewLine()
                    inPane.AddWrappedBoldTextField(Lang('Selected Variant'))
                    if selectedVariant:
                        text = DMVUtils.DriverVariantChoiceName(selectedVariant)
                        inPane.AddWrappedTextField(text)
                    else:
                        inPane.AddWrappedTextField(Lang('No'))

                    inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Select Device Driver") } )
                else:
                    inPane.AddStatusField(Lang("Device Present", 16), "No")

                inPane.NewLine()
                inPane.AddWrappedBoldTextField(Lang('Variant List'))
                for variantText in variantList:
                    inPane.AddWrappedTextField(variantText)
            else:
                # It's unlikely to happen.
                inPane.AddStatusField(Lang("Variants", 16), "No")

    @classmethod
    def PresentActivateHandler(cls):
        Layout.Inst().TopDialogue().ChangeMenu('MENU_PRESENTDRV')

    @classmethod
    def AllActivateHandler(cls):
        drivers = Task.Sync(lambda x: x.xenapi.Host_driver.get_all_records())
        if len(drivers) > 100:
            Layout.Inst().PushDialogue(InfoDialogue(Lang('This feature is unavailable in Pools with more than 100 DMV drivers')))
        else:
            Layout.Inst().TopDialogue().ChangeMenu('MENU_ALLDRV')

    @classmethod
    def InfoActivateHandler(cls, inHandle):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(DriverSelectDialogue(inHandle)))

    @classmethod
    def EmptyHandler(cls, inHandle):
        return

    @classmethod
    def MenuRegenerator(cls, inList, inMenu):
        hw_present_variants = Task.Sync(lambda x: x.xenapi.Driver_variant.get_all_records_where('field "hardware_present" = "true"'))
        hw_present_driverRefs = []
        for variantRef in hw_present_variants:
            variant = hw_present_variants[variantRef]
            if not variant['driver'] in hw_present_driverRefs:
                hw_present_driverRefs.append(variant['driver'])

        retVal = copy.copy(inMenu)
        retVal.RemoveChoices()
        # inList is a list of HotOpaqueRef objects
        driverList = [ HotAccessor().dmv[x] for x in inList ]

        # Sort list by driver name
        driverList.sort(key=lambda driver: driver.friendly_name(''))

        for driver in driverList:
            driverRef = driver.HotOpaqueRef().OpaqueRef()
            nameLabel = driver.friendly_name(Lang('<Unknown>'))
            if driverRef in hw_present_driverRefs:
                retVal.AddChoice(name = nameLabel,
                                 onAction = cls.InfoActivateHandler,
                                 statusUpdateHandler = cls.InfoStatusUpdateHandler,
                                 handle = driver.HotOpaqueRef())
            else:
                retVal.AddChoice(name = nameLabel,
                                 onAction = cls.EmptyHandler,
                                 statusUpdateHandler = cls.InfoStatusUpdateHandler,
                                 handle = driver.HotOpaqueRef())

        if retVal.NumChoices() == 0:
            retVal.AddChoice(name = Lang('<No Multi Version Drivers Present>'),
                                        statusUpdateHandler = cls.NoDMVStatusUpdateHandler)

        return retVal

    @classmethod
    def PresentMenuRegenerator(cls, inName, inMenu):
        hw_present_variants = Task.Sync(lambda x: x.xenapi.Driver_variant.get_all_records_where('field "hardware_present" = "true"'))

        driverRefs = []
        for variantRef in hw_present_variants:
            variant = hw_present_variants[variantRef]
            if not variant['driver'] in driverRefs:
                driverRefs.append(variant['driver'])

        return cls.MenuRegenerator([ HotOpaqueRef(d, 'driver') for d in driverRefs ], inMenu)

    @classmethod
    def AllMenuRegenerator(cls, inName, inMenu):
        return cls.MenuRegenerator(HotAccessor().dmv({}).keys(), inMenu)

    def Register(self):
        Importer.RegisterMenuEntry(
            self,
            'MENU_DMV', # Name of the menu this item is part of
            {
                'menuname' : 'MENU_PRESENTDRV', # Name of the menu this item leads to when selected
                'menutext' : Lang('Available Hardware Driver Variants'),
                'menupriority' : 100,
                'menuregenerator' : XSFeatureDMV.PresentMenuRegenerator,
                'activatehandler' : XSFeatureDMV.PresentActivateHandler,
                'statusupdatehandler' : XSFeatureDMV.PresentStatusUpdateHandler
            }
        )

        Importer.RegisterMenuEntry(
            self,
            'MENU_DMV', # Name of the menu this item is part of
            {
                'menuname' : 'MENU_ALLDRV', # Name of the menu this item leads to when selected
                'menutext' : Lang('All Driver Variants'),
                'menupriority' : 300,
                'menuregenerator' : XSFeatureDMV.AllMenuRegenerator,
                'activatehandler' : XSFeatureDMV.AllActivateHandler,
                'statusupdatehandler' : XSFeatureDMV.AllStatusUpdateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureDMV().Register()
