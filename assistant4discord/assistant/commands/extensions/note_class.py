from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import timestamp_to_utc
import time


class Note(Master):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "notes"
        self.run_on_init = True
        self.noted = ""
        self.created_on = int(time.time())

    def todo(self):
        """ Sets user's previous message as note. """
        c = 0
        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                self.noted = msg.content
                return msg.content

        return None

    def __str__(self):
        return "noted on {}\nnote: {}".format(timestamp_to_utc(self.created_on), self.noted)
