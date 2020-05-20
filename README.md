# Domoticz Plugins Manager

Python plugin for Domoticz to manage other python plugins. This plugin allows you:
- List available and installed plugins
- Install / Update selected Domoticz plugin
- Open plugin repository

Based on [pp-manager](https://github.com/ycahome/pp-manager)

![image](https://user-images.githubusercontent.com/2734836/80870624-4e0f9c00-8cb0-11ea-9e3a-2b16a197f239.png)

## Prerequisites

- Make sure that your Domoticz supports Python plugins (https://www.domoticz.com/wiki/Using_Python_plugins)

## Installation

1. Clone repository into your domoticz plugins folder (make sure that you use `plugins-manager` directory for this plugin, it is really important!)
```
cd domoticz/plugins
git clone https://github.com/stas-demydiuk/domoticz-plugins-manager.git plugins-manager
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "Python Plugins Manager"
4. Refresh Domoticz and in main menu open "Custom\Plugins-Manager"

## Plugin update

1. Go to plugin folder and pull new version
```
cd domoticz/plugins/plugins-manager
git pull
```
2. Restart domoticz

## Registering new plugin in the manager

All available plugins are stored in `plugins.json` file. To add your plugin just add new item to this file following the same structure and then create a pull-request. Plugin item example:

```
"BatteryLevel": {
    "name": "BatteryLevel",
    "author": "999LV",
    "description": "Battery monitoring for Z-Wave nodes",
    "repository": "https://github.com/999LV/BatteryLevel",
    "branch": "master"
},
```