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
        Domoticz.Log('Installing plugin custom page...')

        try:
            source_path = os.path.dirname(os.path.abspath(__file__)) + '/frontend'
            templates_path = os.path.abspath(source_path + '/../../../www/templates')

            Domoticz.Debug('Copying files from ' + source_path + ' to ' + templates_path)

            copy2(source_path + '/index.html', templates_path + '/' + self.ui_name + '.html')
            copy2(source_path + '/index.js', templates_path + '/' + self.ui_name + '.js')

            Domoticz.Log('Installing plugin custom page completed.')
        except Exception as e:
            Domoticz.Error('Error during installing plugin custom page')
            Domoticz.Error(repr(e))

    def uninstall_ui(self):
        Domoticz.Log('Uninstalling plugin custom page...')

        try:
            plugin_path = os.path.dirname(os.path.abspath(__file__))
            templates_path = os.path.abspath(plugin_path + '/../../www/templates/')
            
            if os.path.exists(templates_path + self.ui_name + '.html'):
                os.remove(templates_path + self.ui_name + '.html')

            if os.path.exists(templates_path + self.ui_name + '.js'):
                os.remove(templates_path + self.ui_name + '.js')

            Domoticz.Log('Uninstalling plugin custom page completed.')
        except Exception as e:
            Domoticz.Error('Error during uninstalling plugin custom page')
            Domoticz.Error(repr(e))


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
