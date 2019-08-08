from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import timestamp_to_local
import time


class Note(Master):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        name: str
            Used for identification.
        run_on_init: bool
            If True runs once on initialization.
        noted: str
            User's message used as note string.
        created_on: int
            When did todo() ran.

        """
        super().__init__(**kwargs)
        self.name = "note_it"
        self.run_on_init = True
        self.noted = ""
        self.created_on = int(time.time())

    def todo(self):
        """ Sets user's previous message as note.

        Loop over all messages (newest to oldest) and find author's second message (first is this command).

        Returns
        -------
        str
            Content of message. Set this as note.
        """
        c = 0
        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                self.noted = msg.content
                return msg.content

        return None

    def __str__(self):
        return "noted on {} utc\nnote: {}".format(timestamp_to_local(self.created_on), self.noted)
