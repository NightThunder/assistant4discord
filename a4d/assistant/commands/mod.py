from .extensions.mod_ext import Mod
from .helpers.tui import ShowItems, RemoveItem
from .helpers.mongodb_adder import AddItem
from a4d.assistant.commands.helpers.master import check_if


class Mods(AddItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***Mods help***\n" 
            "Add a moderator. Owner only.\n"
            "Minor bug: owner doesn't count when removing mods (first mod is number 0 etc.)\n" 
            "Call: mod```"
        )
        self.call = "mod"
        self.special = {"hidden": True}

    async def initialize(self):
        """ Initializes owner on start."""
        await self.AddItem_doit(Mod(initialize=True, commands=self.commands, db=self.db))

    @check_if("owner")
    async def doit(self):
        await self.AddItem_doit(Mod)


class ShowMods(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***ShowMods help***\n" 
            "Display all moderators.\n" 
            "Call: show mods```"
        )
        self.call = "show mods"

    async def doit(self):
        await self.ShowItems_doit(Mod, public=True)


class RemoveMod(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveMod help***\n"
            "Removes moderator. Owner only.\n"
            "Call: remove mod <number>```"
        )
        self.call = "remove mod stevilka"
        self.special = {"hidden": True}

    @check_if("owner")
    async def doit(self):
        await self.RemoveItem_doit(Mod)
