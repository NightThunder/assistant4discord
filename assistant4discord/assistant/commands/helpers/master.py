import functools


class Master:

    def __init__(self, client=None, db=None, message=None, commands=None, similarity=None):
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
            {"hidden": bool, "method": "w2v or "tf"}
        saved_channel: int (assigned on reinitialize)
            Channel string loaded from mongodb when reinitialized (if saved_channel then message is None).
        ch_type: int (assigned on reinitialize)
            DMChannel or GroupChannel.

        """
        self.client = client
        self.db = db
        self.message = message
        self.commands = commands
        self.sim = similarity
        self.special = {}
        self.saved_channel = None
        self.ch_type = None

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
            if self.ch_type == "DMChannel":
                # works for discord.py >= 1.2.0
                channel = await self.client.fetch_channel(self.saved_channel)
            else:
                channel = self.client.get_channel(self.saved_channel)

        if is_file:
            await channel.send(file=content)
        else:
            await channel.send(content)


def check_if(arg):
    """ Decorator for checking mod permissions before running command.

    Parameters
    ----------
    arg: str
        Decorator argument ("owner" or "mod").

    References
    ----------
    https://stackoverflow.com/questions/9416947/python-class-based-decorator-with-parameters-that-can-decorate-a-method-or-a-fun
    https://www.youtube.com/watch?v=FsAPt_9Bf3U&feature=youtu.be

    Returns
    -------
    Decorator class.

    """
    class mod_check:
        def __init__(self, fun):
            self.fun = fun

        def __get__(self, obj, objtype):
            return functools.partial(self.__call__, obj)

        async def __call__(self, obj):
            check_rights = await self.check_rights(obj)

            if check_rights is not False:
                return await self.fun(obj)
            else:
                return await self.not_a_mod(obj)

        @staticmethod
        async def not_a_mod(obj):
            """ Dummy function."""
            await obj.send("Higher permission needed!")

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
            """ Verify that user is owner or mod.

            Use in doit as decorator @check_if().

            """
            mod_lst = await self.get_mod_docs(obj)
            owner = mod_lst[0]["mod"]

            if arg == "owner" and str(obj.message.author) == owner:
                return True

            elif arg == "mod":
                for mod in mod_lst:
                    if mod["mod"] == str(obj.message.author):
                        return True
            else:
                return False

    return mod_check
