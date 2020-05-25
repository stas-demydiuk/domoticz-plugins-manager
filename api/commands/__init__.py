from api.commands.list import List
from api.commands.install import Install
from api.commands.uninstall import Uninstall
from api.commands.update import Update

commands = dict({
    'list': List,
    'install': Install,
    'uninstall': Uninstall,
    'update': Update
})
