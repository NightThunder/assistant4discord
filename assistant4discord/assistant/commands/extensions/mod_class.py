from assistant4discord.assistant.commands.master.master_class import Master


class Mod(Master):

    def __init__(self, initialize=False, **kwargs):
        """
        Other Parameters
        ----------------
        name: str
            Used for identification.
        initialize: bool (optional)
        run_on_init: bool
            If True runs once on initialization.
        mod: str
            Name of new mod.
        """
        super().__init__(**kwargs)
        self.name = 'mods'
        self.initialize = initialize
        self.run_on_init = True
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
                pass
            else:
                self.mod = str(app_info.owner)

        else:
            to_mod = self.get_message()

            for user in self.client.users:
                if str(user) == to_mod:
                    self.mod = to_mod
                    return self.mod

            return None

    def get_message(self):
        """ Get mod name from owner's previous message.

        Loop over all messages (newest to oldest) and find author's second message (first is this command).

        Note
        ----
        Expects that only mod name in message. Should be of format <mod name>#<number>.

        Returns
        -------
        str
            New mod name.
        """
        c = 0

        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                to_mod = '{}'.format(msg.content)
                return to_mod

        return None

    def __str__(self):
        return 'bot mod: {}'.format(self.mod)
