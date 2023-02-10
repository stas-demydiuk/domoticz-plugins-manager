import json
import os
from manager import Plugin

plugins = {}

def load(home_folder):
    f = open(home_folder + 'plugins.json')
    plugins_raw = json.load(f)
    plugins_folder = os.path.abspath(home_folder + '../') + '/'

    for key, value in plugins_raw.items():
        plugins[key] = Plugin(plugins_folder, value)
