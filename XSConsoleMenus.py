# Copyright (c) Citrix Systems 2007. All rights reserved.
# xsconsole is proprietary software.
#
# Xen, the Xen logo, XenCenter, XenMotion are trademarks or registered
# trademarks of Citrix Systems, Inc., in the United States and other
# countries.

import sys

from pprint import pprint

from XSConsoleBases import *
from XSConsoleConfig import *
from XSConsoleData import *
from XSConsoleLang import *

class ChoiceDef:
    def __init__(self, name, onAction = None, onEnter = None, priority = None):
        ParamsToAttr()
        self.statusUpdateHandler = None
        
    def StatusUpdateHandler(self):
        return self.statusUpdateHandler
        
    def StatusUpdateHandlerSet(self, inHandler):
        self.statusUpdateHandler = inHandler
        
    def OnAction(self):
        return self.onAction

class Menu:
    def __init__(self, inOwner, inParent, inTitle, inChoiceDefs):
        self.owner = inOwner
        self.parent = inParent
        self.title = inTitle
        self.choiceDefs = inChoiceDefs
        self.choiceIndex = 0
        self.defaultPriority=100
        for choice in self.choiceDefs:
            if choice.priority is None:
                choice.priority = self.defaultPriority
                self.defaultPriority += 100

    def Parent(self): return self.parent
    def Title(self): return self.title
    def ChoiceDefs(self): return self.choiceDefs
    def ChoiceIndex(self): return self.choiceIndex

    def AppendChoiceDef(self, inChoice):
        self.choiceDefs.append(inChoice)

    def AddChoice(self, inChoiceDef, inPriority = None):
        if inPriority is None:
            priority = self.defaultPrority
            self.defaultPrority += 100
        else:
            priority = inPriority
        
        inChoiceDef.priority = priority # FIXME
        self.choiceDefs.append(inChoiceDef)
        
        self.choiceDefs.sort(lambda x, y : cmp(x.priority, y.priority))

    def CurrentChoiceSet(self,  inChoice):
        self.choiceIndex = inChoice
        # Also need to can HandleEnter
        
    def CurrentChoiceDef(self):
        return self.choiceDefs[self.choiceIndex]

    def HandleArrowDown(self):
        self.choiceIndex += 1
        if self.choiceIndex >= len(self.choiceDefs):
            self.choiceIndex = 0
        self.HandleEnter()
        return True

    def HandleArrowUp(self):
        if self.choiceIndex == 0:
            self.choiceIndex = len(self.choiceDefs) - 1
        else:
            self.choiceIndex -= 1
        self.HandleEnter()
        return True

    def HandleArrowLeft(self):
        if self.parent:
            self.owner.ChangeMenu(self.parent)
            handled = True
        else:
            handled = False
        return handled

    def HandleEnter(self):
        if callable(self.CurrentChoiceDef().onEnter):
            self.CurrentChoiceDef().onEnter()
        return True

    def HandleSelect(self):
        if callable(self.CurrentChoiceDef().onAction):
            self.CurrentChoiceDef().onAction()
        return True

    def HandleKey(self, inKey):
        if inKey == 'KEY_DOWN':
            handled = self.HandleArrowDown()
        elif inKey == 'KEY_UP':
            handled = self.HandleArrowUp()
        elif inKey == 'KEY_LEFT' or inKey == 'KEY_ESCAPE':
            handled = self.HandleArrowLeft()
        elif inKey == 'KEY_ENTER' or inKey == 'KEY_RIGHT':
            handled = self.HandleSelect()
        else:
            handled = False
        
        return handled
        
class RootMenu:
    def __init__(self, inDialogue):
        rootMenu = Menu(self, None, Lang("Customize System"), [
            ChoiceDef(Lang("Status Display"), 
                None,  lambda : inDialogue.ChangeStatus('STATUS')),
            ChoiceDef(Lang("Network and Management Interface"), 
                lambda : inDialogue.ChangeMenu('MENU_NETWORK'), lambda : inDialogue.ChangeStatus('NETWORK')),
            ChoiceDef(Lang("Authentication"), 
                lambda: inDialogue.ChangeMenu('MENU_AUTH'), lambda : inDialogue.ChangeStatus('AUTH')),
            ChoiceDef(Lang("XenServer Details and Licensing"), 
                lambda : inDialogue.ChangeMenu('MENU_XENDETAILS'), lambda : inDialogue.ChangeStatus('XENDETAILS')),
            ChoiceDef(Lang("Hardware and BIOS Information"), 
                lambda : inDialogue.ChangeMenu('MENU_PROPERTIES'), lambda : inDialogue.ChangeStatus('PROPERTIES')),          
            ChoiceDef(Lang("Keyboard and Timezone"), 
                lambda : inDialogue.ChangeMenu('MENU_MANAGEMENT'), lambda : inDialogue.ChangeStatus('MANAGEMENT')),
            ChoiceDef(Lang("Disks and Storage Repositories"), 
                lambda : inDialogue.ChangeMenu('MENU_DISK'), lambda : inDialogue.ChangeStatus('DISK')),
            ChoiceDef(Lang("Remote Service Configuration"), 
                lambda : inDialogue.ChangeMenu('MENU_REMOTE'), lambda : inDialogue.ChangeStatus('REMOTE')),
            ChoiceDef(Lang("Backup, Restore and Update"), 
                lambda : inDialogue.ChangeMenu('MENU_BUR'), lambda : inDialogue.ChangeStatus('BUR')),
            ChoiceDef(Lang("Technical Support"), 
                lambda : inDialogue.ChangeMenu('MENU_TECHNICAL'), lambda : inDialogue.ChangeStatus('TECHNICAL')),
            ChoiceDef(Lang("Reboot or Shutdown"), 
                lambda : inDialogue.ChangeMenu('MENU_REBOOT'), lambda : inDialogue.ChangeStatus('REBOOTSHUTDOWN')),
            ChoiceDef(Lang("Local Command Shell"), 
                lambda : inDialogue.ActivateDialogue('DIALOGUE_LOCALSHELL'), lambda : inDialogue.ChangeStatus('LOCALSHELL'))
        ])
        
         # When started from inittab, mingetty adds -f root to the command, so use this to suppress the Quit choice
        if not '-f' in sys.argv:
            rootMenu.AppendChoiceDef(ChoiceDef(Lang("Quit"), 
                lambda : inDialogue.ActivateDialogue('DIALOGUE_QUIT'), lambda : inDialogue.ChangeStatus('QUIT'), 10000))
        
        rebootText = Lang("Reboot Server")
        
        propertiesChoices = [
                ChoiceDef(Lang("System Description"), None, lambda : inDialogue.ChangeStatus('SYSTEM')),
                ChoiceDef(Lang("Processor"), None, lambda : inDialogue.ChangeStatus('PROCESSOR')),
                ChoiceDef(Lang("System Memory"), None, lambda : inDialogue.ChangeStatus('MEMORY')),
                ChoiceDef(Lang("Local Storage Controllers"), None, lambda : inDialogue.ChangeStatus('STORAGE')),
                ChoiceDef(Lang("BIOS Information"), None, lambda : inDialogue.ChangeStatus('BIOS'))
            ]

        if Data.Inst().bmc.version('') != '':
           propertiesChoices.append(ChoiceDef(Lang("BMC Version"), None, lambda : inDialogue.ChangeStatus('BMC')))
           
        if Data.Inst().cpld.version('') != '':
            propertiesChoices.append(ChoiceDef(Lang("CPLD Version"), None, lambda : inDialogue.ChangeStatus('CPLD')))
        
        burChoices = [
            ChoiceDef(Lang("Apply Update"), lambda: inDialogue.ActivateDialogue('DIALOGUE_PATCH'),
                lambda : inDialogue.ChangeStatus('PATCH')),
            ChoiceDef(Lang("Backup Server State"), lambda: inDialogue.ActivateDialogue('DIALOGUE_BACKUP'),
                lambda : inDialogue.ChangeStatus('BACKUP')),
            ChoiceDef(Lang("Restore Server State From Backup"), lambda: inDialogue.ActivateDialogue('DIALOGUE_RESTORE'),
                lambda : inDialogue.ChangeStatus('RESTORE'))
        ]
            
        if Data.Inst().backup.canrevert(False):
            burChoices.append(ChoiceDef(Lang("Revert to Pre-Upgrade Version"), lambda: inDialogue.ActivateDialogue('DIALOGUE_REVERT'),
                lambda : inDialogue.ChangeStatus('REVERT')))
        
        self.menus = {
            'MENU_ROOT' : rootMenu,
            
            'MENU_PROPERTIES' : Menu(self, 'MENU_ROOT', Lang("Hardware and BIOS Information"), propertiesChoices),

            'MENU_NETWORK' : Menu(self, 'MENU_ROOT', Lang("Network and Management Interface"), [
                # Configure Management Interface is in a plugin
                ChoiceDef(Lang("Add/Remove DNS Servers"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_DNS'), lambda : inDialogue.ChangeStatus('DNS')),
                # Hostname option removed - now subsumed into Configure Management Interface
                ChoiceDef(Lang("Network Time (NTP)"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_NTP'), lambda : inDialogue.ChangeStatus('NTP')),
                ChoiceDef(Lang("Test Network"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_TESTNETWORK'), lambda : inDialogue.ChangeStatus('TESTNETWORK')),
                ChoiceDef(Lang("Display NICs"), None, lambda : inDialogue.ChangeStatus('PIF'))
            ]),
 
            'MENU_MANAGEMENT' : Menu(self, 'MENU_ROOT', Lang("Keyboard Langauge and Timezone"), [
                ChoiceDef(Lang("Keyboard Language and Layout"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_KEYBOARD'), lambda : inDialogue.ChangeStatus('KEYBOARD')),
                ChoiceDef(Lang("Set Timezone"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_TIMEZONE'), lambda : inDialogue.ChangeStatus('TIMEZONE'))
            ]),

            'MENU_REMOTE' : Menu(self, 'MENU_ROOT', Lang("Remote Service Configuration"), [
                ChoiceDef(Lang("Enable/Disable Remote Shell"), lambda: inDialogue.ActivateDialogue('DIALOGUE_REMOTESHELL'),
                    lambda : inDialogue.ChangeStatus('REMOTESHELL')),
                ChoiceDef(Lang("Remote Logging (syslog)"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_SYSLOG'), lambda : inDialogue.ChangeStatus('SYSLOG')),
                ChoiceDef(Lang("Setup Remote Database"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_REMOTEDB'), lambda : inDialogue.ChangeStatus('REMOTEDB'))
            ]),

            'MENU_AUTH' : Menu(self, 'MENU_ROOT', Lang("Authentication"), [
                ChoiceDef(Lang("Log In/Out"), lambda : inDialogue.HandleLogInOut(), lambda : inDialogue.ChangeStatus('LOGINOUT')),
                ChoiceDef(Lang("Change Password"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_CHANGEPASSWORD'),
                    lambda : inDialogue.ChangeStatus('CHANGEPASSWORD')),
                ChoiceDef(Lang("Change Auto-Logout Time"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_CHANGETIMEOUT'),
                    lambda : inDialogue.ChangeStatus('CHANGETIMEOUT'))
            ]), 
 
            'MENU_XENDETAILS' : Menu(self, 'MENU_ROOT', Lang("XenServer Details"), [
                ChoiceDef(Lang("Install XenServer License"), 
                    lambda : inDialogue.ActivateDialogue('DIALOGUE_INSTALLLICENCE'), lambda : inDialogue.ChangeStatus('INSTALLLICENCE')),
            ]),

            'MENU_DISK' : Menu(self, 'MENU_ROOT', Lang("Disks and Storage Repositories"), [
                ChoiceDef(Lang("Claim Local Disk as SR"), 
                    lambda : inDialogue.ActivateDialogue('DIALOGUE_CLAIMSR'), lambda : inDialogue.ChangeStatus('CLAIMSR')),
                ChoiceDef(Lang("Specify Suspend SR"), lambda: inDialogue.ActivateDialogue('DIALOGUE_SUSPENDSR'),
                    lambda : inDialogue.ChangeStatus('SUSPENDSR')),
                ChoiceDef(Lang("Specify Crash Dump SR"),
                    lambda: inDialogue.ActivateDialogue('DIALOGUE_CRASHDUMPSR'), lambda : inDialogue.ChangeStatus('CRASHDUMPSR')),
                    
                ChoiceDef(Lang("View Local Storage Controllers"), None, lambda : inDialogue.ChangeStatus('STORAGE')),
            ]),
            
            'MENU_BUR' : Menu(self, 'MENU_ROOT', Lang("Backup, Restore and Update"), burChoices),
                
            'MENU_TECHNICAL' : Menu(self, 'MENU_ROOT', Lang("Technical Support"), [
                ChoiceDef(Lang("Validate Server Configuration"), lambda: inDialogue.ActivateDialogue('DIALOGUE_VALIDATE'),
                    lambda : inDialogue.ChangeStatus('VALIDATE')),
                # Upload bug report removed (CA-13345)
                # ChoiceDef(Lang("Upload Bug Report"), lambda: inDialogue.ActivateDialogue('DIALOGUE_BUGREPORT'),
                #    lambda : inDialogue.ChangeStatus('BUGREPORT')) ,
                ChoiceDef(Lang("Save Bug Report"), lambda: inDialogue.ActivateDialogue('DIALOGUE_SAVEBUGREPORT'),
                    lambda : inDialogue.ChangeStatus('SAVEBUGREPORT')),
                ChoiceDef(Lang("Enable/Disable Verbose Boot Mode"), lambda: inDialogue.ActivateDialogue('DIALOGUE_VERBOSEBOOT'),
                    lambda : inDialogue.ChangeStatus('VERBOSEBOOT')),
                ChoiceDef(Lang("Reset to Factory Defaults"), lambda: inDialogue.ActivateDialogue('DIALOGUE_RESET'),
                    lambda : inDialogue.ChangeStatus('RESET'))
            ]), 
     
            'MENU_REBOOT' : Menu(self, 'MENU_ROOT', Lang("Reboot"), [
                    ChoiceDef(rebootText, 
                        lambda : inDialogue.ActivateDialogue('DIALOGUE_REBOOT'), lambda : inDialogue.ChangeStatus('REBOOT')), 
                    ChoiceDef(Lang("Shutdown Server"), 
                        lambda : inDialogue.ActivateDialogue('DIALOGUE_SHUTDOWN'), lambda : inDialogue.ChangeStatus('SHUTDOWN')), 
            ])
        }
        
        self.currentKey = 'MENU_ROOT'
    
    def CurrentMenu(self):
        return self.menus[self.currentKey]

    def ChangeMenu(self, inKey):
        self.currentKey = inKey
        self.CurrentMenu().HandleEnter()

    def Reset(self):
        self.currentKey = 'MENU_ROOT'
        
        for menu in self.menus.values():
            menu.CurrentChoiceSet(0)
            
        self.CurrentMenu().HandleEnter()
        
    def AddChoice(self, inMenuName, inChoiceDef, inPriority = None):
        if not self.menus.has_key(inMenuName):
            raise Exception(Lang("Unknown menu '")+inMenuName+"'")
        
        self.menus[inMenuName].AddChoice(inChoiceDef, inPriority)
