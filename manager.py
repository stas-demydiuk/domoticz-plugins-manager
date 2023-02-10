import Domoticz
import os
import subprocess
from shutil import rmtree


class Plugin():
    def __init__(self, plugins_folder, plugin_data):
        self.name = plugin_data['name']
        self.author = plugin_data['author']
        self.description = plugin_data['description']
        self.repository = plugin_data['repository']
        self.branch = plugin_data['branch']
        self.folder_name = plugin_data['folder']

        self.plugin_folder = str(plugins_folder + self.folder_name)

    def is_installed(self):
        return os.path.isdir(self.plugin_folder) == True

    def is_update_available(self):
        Domoticz.Debug('Checking plugin "' + self.name + '" for updates')

        if (self.is_installed() == False):
            return False

        ppGitFetch="LANG=en_US /usr/bin/git fetch"
        try:
            prFetch=subprocess.Popen(ppGitFetch, cwd = self.plugin_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (outFetch, errorFetch)=prFetch.communicate()

            if outFetch:
                Domoticz.Debug("Git Response:" + str(outFetch))
            if errorFetch:
                Domoticz.Debug("Git Error:" + str(errorFetch.strip()))
        
        except OSError as eFetch:
            Domoticz.Error("Git ErrorNo:" + str(eFetch.errno))
            Domoticz.Error("Git StrError:" + str(eFetch.strerror))


        ppUrl="LANG=en_US /usr/bin/git status -uno"
        Domoticz.Debug("Calling:" + ppUrl + " on folder " + self.plugin_folder)

        try:
            pr=subprocess.Popen(ppUrl, cwd = self.plugin_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (out, error)=pr.communicate()

            if out:
                Domoticz.Debug("Git Response:" + str(out))

                if (str(out).find("up-to-date") != -1) or (str(out).find("up to date") != -1):
                    return False
                elif (str(out).find("Your branch is behind") != -1) and (str(str(out).find("error")) == "-1"):
                    return True
                elif (str(out).find("Your branch is ahead") != -1) and (str(str(out).find("error")) == "-1"):
                    return False
                else:
                    Domoticz.Error('Something went wrong during plugin "' + self.name + '" update')
                    return None

            if error:
                Domoticz.Debug("Git Error:" + str(error.strip()))
                
                if str(error).find("Not a git repository") != -1:
                    Domoticz.Log('Plugin "' + self.name + '" is not installed from gitHub. Ignoring!.')

        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))

        return None

    def install(self):
        Domoticz.Log("Installing Plugin:" + self.description)

        if (self.is_installed()):
            return True
        
        plugins_folder = os.path.dirname(str(os.getcwd()) + "/plugins/")
        repository = self.repository + ".git"
        clone_cmd="LANG=en_US /usr/bin/git clone -b " + self.branch + " " + repository + " " + self.folder_name
        Domoticz.Debug("Calling: " + clone_cmd)

        try:
            pr=subprocess.Popen(clone_cmd, cwd = plugins_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (out, error)=pr.communicate()

            if out:
                Domoticz.Log("Succesfully installed:" + str(out).strip)
                Domoticz.Log("---Restarting Domoticz MAY BE REQUIRED to activate new plugins---")
                return True

            if error:
                Domoticz.Debug("Git Error:" + str(error))
                
                if str(error).find("Cloning into") != -1:
                    Domoticz.Log("Plugin " + self.description + " installed Succesfully")
                    return True

        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))
        
        return False

    def update(self):
        Domoticz.Log("Updating Plugin:" + self.description)

        if (not self.is_update_available()):
            return True

        cmd = "LANG=en_US /usr/bin/git pull --force"
        Domoticz.Debug('Calling: "' + cmd + '" on folder ' + self.plugin_folder)

        try:
            pr = subprocess.Popen(cmd, cwd = self.plugin_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (out, error) = pr.communicate()

            if out:
                Domoticz.Debug("Git Response:" + str(out))
                if (str(out).find("Already up-to-date") != -1) or (str(out).find("Already up to date") != -1):
                   Domoticz.Debug('Plugin "' + self.description + '" already Up-To-Date')
                   return True
                elif (str(out).find("Updating") != -1) and (str(str(out).find("error")) == "-1"):
                   Domoticz.Log("Succesfully pulled gitHub update:" + str(out)[str(out).find("Updating")+8:26] + " for plugin " + self.description)
                   Domoticz.Log("---Restarting Domoticz MAY BE REQUIRED to activate new plugins---")
                   return True
                else:
                   Domoticz.Error("Something went wrong with update of " + self.description)

            if error:
                Domoticz.Debug("Git Error:" + str(error.strip()))
                if str(error).find("Not a git repository") != -1:
                   Domoticz.Error("Plugin: " + self.description + " is not installed from gitHub. Cannot be updated with PP-Manager!!.")

        except OSError as e:
            Domoticz.Error("Git ErrorNo:" + str(e.errno))
            Domoticz.Error("Git StrError:" + str(e.strerror))

        return False

    def uninstall(self):
        Domoticz.Log("Uninstalling Plugin:" + self.description)

        if not self.is_installed():
            return True

        try:
            rmtree(self.plugin_folder)
            return True
        except Exception as e:
            Domoticz.Error(repr(e))

        return False