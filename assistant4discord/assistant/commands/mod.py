from assistant4discord.assistant.commands.mod_helper.mod_class import Mod
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class Mods(AddItem):

    def __init__(self):
        super().__init__()
        self.help = "```***Mods help***\n" "Add a moderator. Owner only.```"
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
        self.help = "```***ShowMods help***\n" "Display all moderators.```"
        self.call = "show mods"

    async def doit(self):
        await self.ShowItems_doit("Mods", public=True)


class RemoveMod(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = "```***RemoveMod help***\n" "Removes moderator. Owner only.```"
        self.call = "remove mod stevilka"
        self.special = {"permission": "owner", "hidden": True}

    async def doit(self):
        if self.check_rights():
            await self.RemoveItem_doit("Mods")
        else:
            await self.message.channel.send("need to be {}".format(self.special["permission"]))
