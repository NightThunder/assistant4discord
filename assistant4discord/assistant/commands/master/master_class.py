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
            {"command str": command obj, ...}
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


class mod_check:
    """ Decorator for checking permission in special attribute of command."""

    def __init__(self, original_function):
        self.original_function = original_function

    def __get__(self, obj, objtype):
        import functools
        return functools.partial(self.__call__, obj)

    async def __call__(self, obj):
        check_rights = await self.check_rights(obj)

        if check_rights is not False:
            return await self.original_function(obj)
        else:
            return await self.not_a_mod(obj)

    @staticmethod
    async def not_a_mod(obj):
        await obj.message.channel.send("Higher permission needed!")

    @staticmethod
    async def get_mod_docs(obj):
        """ Get all documents of a collection.

        Returns
        -------
        All documents in a collection as a list of dicts.

        """
        cursor = obj.db["mods"].find({})
        return await cursor.to_list(length=None)

    async def check_rights(self, obj):
        """ Verify that user owner or mod.

        Use in doit with special for command blocking.

        """
        mod_lst = await self.get_mod_docs(obj)
        owner = mod_lst[0]["mod"]

        if obj.special.get("permission") == "owner" and str(obj.message.author) == owner:
            return True

        elif obj.special.get("permission") == "mod":
            for mod in mod_lst:
                if mod["mod"] == str(obj.message.author):
                    return True
        else:
            return False
