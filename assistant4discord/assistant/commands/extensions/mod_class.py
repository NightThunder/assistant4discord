from assistant4discord.assistant.commands.master.master_class import Master


class Mod(Master):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'mods'
        self.run_on_init = True
        self.mod = None
        self.n = 0

    async def todo(self):
        """ Set a moderator.

        If n == 0 get owner name from info command (await client.application_info()). Look in database if owner already
        present, if owner not found set owner as mod.
        If n!= 0 check all users that bot can see for a match. If match found set new mod.

        Returns
        -------
        str
            Name of a new mod or None if user not found.
        """
        if self.n == 0:
            app_info = await self.commands["AppInfo"].get_app_info()

            collection = self.db[self.name]
            owner_in_db = await collection.find_one({'mod': str(app_info.owner)})

            if owner_in_db:
                pass
            else:
                self.mod = str(app_info.owner)

            self.n += 1

        else:
            to_mod = self.get_message()

            for user in self.client.users:
                if str(user) == to_mod:
                    self.mod = to_mod
                    return self.mod

            return None

    def get_message(self):
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
