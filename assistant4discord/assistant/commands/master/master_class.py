class Master:

    def __init__(self, client=None, db=None, message=None, commands=None, similarity=None, saved_channel=None):
        """ Base class for commands.

        Parameters
        ----------
        client: obj
            Discord object (see docs).
        db: obj
            Mongodb database (see docs).
        message: obj
            Discord object (see docs).
        commands: dict
            {'command str': command obj, ...}
        similarity: obj
            Command recognition functionality.

        Other Parameters
        ----------------
        special: dict
            {"permission": "owner" or "mod", "hidden": bool, "method": "w2v or "tf"}
        saved_channel: str
            Channel string loaded from mongodb when reinitialized (if saved_channel then message is None).

        """
        self.client = client
        self.db = db
        self.message = message
        self.commands = commands
        self.sim = similarity
        self.special = {}
        self.saved_channel = saved_channel

    async def get_all_docs(self, collection_name):
        """ Get all documents of a collection.

        TODO: move all mongodb methods here

        Returns
        -------
        All documents in a collection as a list of dicts.

        """
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def check_rights(self):
        """ Verify that user owner or mod.

        Use in doit with special for command blocking.

        """
        mod_lst = await self.get_all_docs('Mods'.lower())
        owner = mod_lst[0]['mod']

        if self.special.get("permission") == "owner" and str(self.message.author) == owner:
            return True

        elif self.special.get("permission") == 'mod':
            for mod in mod_lst:
                if mod['mod'] == str(self.message.author):
                    return True

        else:
            return False

    async def send(self, content, is_file=False):
        """ Send message to discord channel.

        Parameters
        ----------
        content: str or discord.File
        is_file: bool (optional)

        """
        if self.message:
            channel = self.client.get_channel(self.message.channel.id)
        else:
            channel = self.client.get_channel(self.saved_channel)

        if is_file:
            await channel.send(file=content)
        else:
            await channel.send(content)
