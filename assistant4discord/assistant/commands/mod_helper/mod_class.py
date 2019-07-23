from assistant4discord.assistant.commands.master.master_class import Master


class Mod(Master):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.run_on_init = True
        self.to_mod = None

    def to_do(self):
        """ Set a moderator.

        Checks all users that bot can see for a match.

        Returns
        -------
        str
            Name of new mod or None user not found.
        """
        to_mod = self.get_message()

        for user in self.client.users:
            if str(user) == to_mod:
                self.to_mod = to_mod
                return self.to_mod

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
        return 'bot mod: {}'.format(self.to_mod)
