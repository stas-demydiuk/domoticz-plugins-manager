"""
<plugin key="plugins-manager" name="Python Plugins Manager" version="1.0.0">
    <description>
		<h2>Python Plugins Manager v.1.0.0</h2><br/>
		<h3>Features:</h3>
		<ul style="list-style-type:square">
			<li>List available and installed plugins</li>
			<li>Install / Update selected Domoticz plugin</li>
            <li>Open plugin repository</li>
		</ul>
    </description>
     <params>
         <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import platform
import os
from shutil import copy2
from plugins import plugins
from api import APIManager


class BasePlugin:
    def __init__(self):
        self.ui_name = 'plugins-manager'
        self.plugin_folder = 'plugins-manager'

    def onStart(self):
        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debugging(2)
        else:
            Domoticz.Debugging(0)

        if platform.system() == "Windows":
            Domoticz.Error("Windows Platform is NOT YET SUPPORTED!")
            return

        self.install_ui()
        self.api_manager = APIManager(Devices)

    def onStop(self):
        self.uninstall_ui()

    def onDeviceModified(self, unit):
        if (unit == self.api_manager.unit):
            self.api_manager.handle_request(Devices[unit].sValue)
            return

    def install_ui(self):
        Domoticz.Debug('Installing plugin custom page...')

        copy2('./plugins/' + self.plugin_folder + '/frontend/index.html',
              './www/templates/' + self.ui_name + '.html')
        copy2('./plugins/' + self.plugin_folder + '/frontend/index.js',
              './www/templates/' + self.ui_name + '.js')

        Domoticz.Debug('Installing plugin custom page completed.')

    def uninstall_ui(self):
        Domoticz.Debug('Uninstalling plugin page...')

        if os.path.exists('./www/templates/' + self.ui_name + '.html'):
            os.remove('./www/templates/' + self.ui_name + '.html')

        if os.path.exists('./www/templates/' + self.ui_name + '.js'):
            os.remove('./www/templates/' + self.ui_name + '.js')

        Domoticz.Debug('Uninstalling plugin custom page completed.')


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)
