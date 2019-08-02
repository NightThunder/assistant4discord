from .extensions.mod_class import Mod
from .extensions.helpers.tui import ShowItems, RemoveItem
from .extensions.helpers.mongodb_adder import AddItem


class Mods(AddItem):
    def __init__(self):
        super().__init__()
        self.help = ("```***Mods help***\n" 
                     "Add a moderator. Owner only.\n" 
                     "Call: mod```"
        )
        self.call = "mod"
        self.special = {"permission": "owner", "hidden": True}

    async def initialize(self):
        """ Initializes owner on start."""
        await self.AddItem_doit(Mod(commands=self.commands, db=self.db))

    async def doit(self):
        if self.check_rights():
            await self.AddItem_doit(Mod)
        else:
            await self.message.channel.send("need to be {}".format(self.special["permission"]))


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
        await self.ShowItems_doit("Mods", public=True)


class RemoveMod(RemoveItem):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveMod help***\n"
            "Removes moderator. Owner only.\n"
            "Call: remove mod <number>```"
        )
        self.call = "remove mod stevilka"
        self.special = {"permission": "owner", "hidden": True}

    async def doit(self):
        if self.check_rights():
            await self.RemoveItem_doit("Mods")
        else:
            await self.message.channel.send("need to be {}".format(self.special["permission"]))
