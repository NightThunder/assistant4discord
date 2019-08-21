import time
from assistant4discord.assistant.commands.helpers.master import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder


class ExtError(Exception):
    """ Custom exception for extensions."""
    pass


class Extend(Master):

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        name: str
            Used for identification.
        run_on_init: bool
            If True runs once on initialization.
        use_asyncio: bool
            True if asyncio is needed.
        time_to_message: int (optional)
            Seconds to message.
        every: bool (optional)
            True if repeated (do again after sleep).
        switch: int (optional)
            0 if never ran, 1 if ran once or more.
        created_on: int
            When was init created (when did doit() first run).

        Note
        ----
        All None attributes in __init__ are initialized in doit() method.

        """
        super().__init__(**kwargs)
        self.name = None
        self.run_on_init = True
        self.use_asyncio = False
        self.time_to_message = None
        self.every = None
        self.switch = 0
        self.created_on = int(time.time())

    def get_message(self):
        """ Get message from discord.

        Loop over all messages (newest to oldest) and find author's second message (first is this command).

        Returns
        -------
        str
            Author's last message in chat.
        """
        c = 0

        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                return msg.content

        raise ExtError('No previous message found!')

    def time_message(self):
        time_to_command, every = sent_time_finder(self.message.content)

        if time_to_command is None:
            raise ExtError("Time in the past!")
        else:
            return time_to_command, every
