from api.api_command import APICommand
from plugins import plugins


class Install(APICommand):
    def execute(self, params):
        if isinstance(params, dict):
            plugin_key = params.get('plugin')
            branch = params.get('branch')
        else:
            plugin_key = params
            branch = None

        if plugin_key not in plugins:
            self.send_error('Plugin not found')
            return None

        plugin = plugins[plugin_key]

        if plugin.install(branch):
            self.send_response('Plugin has been succesfully installed. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occured during plugin installation. Please check Domoticz Log for more details.')
