from api.api_command import APICommand
from plugins import plugins
import Domoticz


class Install(APICommand):
    def execute(self, params):
        if isinstance(params, dict):
            plugin_key = params.get('key')
            branch = params.get('branch')
        else:
            plugin_key = params
            branch = None

        Domoticz.Log(f"Received install request for plugin: {plugin_key}, branch: {branch}")

        if plugin_key not in plugins:
            self.send_error(f'Plugin {plugin_key} not found')
            return None

        plugin = plugins[plugin_key]

        if plugin.install(branch):
            self.send_response('Plugin has been successfully installed. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occurred during plugin installation. Please check Domoticz Log for more details.')
