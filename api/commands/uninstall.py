from api.api_command import APICommand
from plugins import plugins


class Uninstall(APICommand):
    def execute(self, params):
        if params not in plugins:
            self.send_error('Plugin not found')
            return None

        plugin = plugins[params]

        if (plugin.uninstall()):
            self.send_response('Plugin has been succesfully uninstalled. Please restart Domoticz to take effect.')
        else:
            self.send_error('Error occured during plugin uninstallation. Please check Domoticz Log for more details.')
