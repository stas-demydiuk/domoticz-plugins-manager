from api.api_command import APICommand
from plugins import plugins
import Domoticz


class Install(APICommand):
    def execute(self, params):
        if isinstance(params, dict):
            plugin_key = params.get('plugin')
            branch = params.get('branch')
        else:
            plugin_key = params
            branch = None

        Domoticz.Log(f'Executing install command with plugin_key: {plugin_key}, branch: {branch}')

        if plugin_key not in plugins:
            Domoticz.Error(f'Plugin {plugin_key} not found')
            self.send_error('Plugin not found')
            return None

        plugin = plugins[plugin_key]

        if plugin.install(branch):
            self.send_response('Plugin has been succesfully installed. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occured during plugin installation. Please check Domoticz Log for more details.')
