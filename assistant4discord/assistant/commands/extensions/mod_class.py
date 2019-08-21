from assistant4discord.assistant.commands.helpers.extend import Extend, ExtError


class Mod(Extend):

    def __init__(self, initialize=False, **kwargs):
        """
        Other Parameters
        ----------------
        initialize: bool (optional)
        mod: str
            Name of new mod.
        """
        super().__init__(**kwargs)
        self.name = 'mods'
        self.initialize = initialize
        self.mod = None

    async def doit(self):
        """ Set a moderator.

        If initialize get owner name from info command (await client.application_info()). Look in database if owner already
        present, if owner not found create mod collection and write owner as mod to it.
        Else check all users that bot can see for a match. If match found set new mod.

        Returns
        -------
        str
            Name of a new mod or None if user not found.
        """
        if self.initialize:
            app_info = await self.commands["AppInfo"].get_app_info()

            collection = self.db[self.name.lower()]
            owner_in_db = await collection.find_one({'mod': str(app_info.owner)})

            if owner_in_db:
                raise ExtError
            else:
                self.mod = str(app_info.owner)

        else:
            to_mod = self.get_message()

            for user in self.client.users:
                if str(user) == to_mod:
                    self.mod = to_mod
                    return self.mod

            raise ExtError("Could not find user!")

    def __str__(self):
        return 'bot mod: {}'.format(self.mod)
