from api.api_command import APICommand
from plugins import plugins


class List(APICommand):
    def execute(self, params):
        response = {}

        for key, plugin in plugins.items():
            response[key] = {
                'key': key,
                'author': plugin.author,
                'description': plugin.description,
                'name': plugin.name,
                'source': plugin.repository + '/tree/' + plugin.branch[0],
                'branches': plugin.branch,
                'is_installed': plugin.is_installed(),
                'is_update_available': plugin.is_update_available(),
            }

        self.send_response(response)
