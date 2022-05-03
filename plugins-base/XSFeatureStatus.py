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

def is_master():
    """ Reads pool.conf and return whether or not this host is the pool master.
        Raises an exception if the file couldn't be read.
    """
    with open('%s/pool.conf' % (Config.Inst().XCPConfigDir()), 'r') as fd:
        items = fd.readline().split(':')
        return items[0].strip() == 'master'

class XSFeatureStatus:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()

        inPane.AddWrappedTextField(data.dmi.system_manufacturer())
        inPane.AddWrappedTextField(data.dmi.system_product_name())
        inPane.NewLine()
        inPane.AddWrappedTextField(Language.Inst().Branding(data.derived.brand()) + ' ' +
            data.derived.coreversion())
        inPane.NewLine()
        inPane.AddTitleField(Lang("Management Network Parameters"))
        
        if len(data.derived.managementpifs([])) == 0:
            db = HotAccessor()
            try:
                is_not_master = not is_master()
            except Exception as e:
                inPane.AddWrappedTextField(Lang("`pool.conf` couldn't be read: %s" % e))
            else:
                if not data.IsXAPIRunning():
                    inPane.AddWrappedTextField(Lang("XAPI service is not running."))
                elif db.host(None) is not None:
                    inPane.AddWrappedTextField(Lang("Finishing start-up."))
                elif is_not_master:
                    inPane.AddWrappedTextField(Lang("Pool master is unreachable."))
                else:
                    inPane.AddWrappedTextField(Lang("<No network configured>"))
        else:
            inPane.AddStatusField(Lang('Device', 16), data.derived.managementpifs()[0]['device'])
            if int(data.derived.managementpifs()[0]['VLAN']) >= 0:
                inPane.AddStatusField(Lang('VLAN', 16), data.derived.managementpifs()[0]['VLAN'])
            inPane.AddStatusField(Lang('IP address', 16), data.ManagementIP(''))
            inPane.AddStatusField(Lang('Netmask', 16),  data.ManagementNetmask(''))
            inPane.AddStatusField(Lang('Gateway', 16),  data.ManagementGateway(''))
        
        inPane.NewLine()
        inPane.AddWrappedTextField(Lang('Press <Enter> to display the SSL key fingerprints for this host'))
    
        inPane.AddKeyHelpField( { Lang("<F5>") : Lang("Refresh"), Lang("<Enter>") : Lang("Fingerprints")})

    @classmethod
    def ActivateHandler(cls):
        data = Data.Inst()
        appName = data.derived.app_name('')

        message = ''
        message += Lang('Key fingerprint shown when connecting from '+appName+' (https)\n\n')
        message += data.sslfingerprint('')+'\n\n'
        message += Lang('Key fingerprint shown when logging in remotely (ssh)\n\n')
        message += data.sshfingerprint('')

        Layout.Inst().PushDialogue(InfoDialogue(Lang("SSL Key Fingerprints"), message))

    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'STATUS', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_ROOT',
                'menupriority' : 50,
                'menutext' : Lang('Status Display'),
                'statusupdatehandler' : XSFeatureStatus.StatusUpdateHandler,
                'activatehandler' : XSFeatureStatus.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureStatus().Register()
