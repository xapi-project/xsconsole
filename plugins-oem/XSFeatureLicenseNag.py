# Copyright (c) 2015 Citrix Systems Inc.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

if __name__ == "__main__":
    raise Exception("This script is a plugin for xsconsole and cannot run independently")

from XSConsoleStandard import *

class XSFeatureLicenseNag:
    @classmethod
    def ReadyHandler(cls):
        data = Data.Inst()

        if data.host.edition('') == 'basic':
            message = Lang("""For more help:
http://www.inspur.com/lcjtww/443018/2252797/index.html

Purchase consulting: 400-860-6708\t\t\t\t\t\t\t\t800-860-6708
""")
            Layout.Inst().PushDialogue(InfoDialogue(Lang('Welcome'), message))

    def Register(self):
        data = Data.Inst()
        appName = data.derived.app_name('')
        fullAppName = data.derived.full_app_name('')
        Importer.RegisterNamedPlugIn(
            self,
            'LICENSE_NAG', # Key of this plugin for replacement, etc.
            {
                'readyhandler' : XSFeatureLicenseNag.ReadyHandler,
                'readyhandlerpriority' : 1200,
            }
        )

# Register this plugin when module is imported
XSFeatureLicenseNag().Register()
