import json
from manager import Plugin

f = open('./plugins/plugins-manager/plugins.json',)
plugins_raw = json.load(f)
plugins = {}

for key, value in plugins_raw.items():
    plugins[key] = Plugin(key, value)
