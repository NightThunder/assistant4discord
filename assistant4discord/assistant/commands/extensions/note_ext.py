from assistant4discord.assistant.commands.helpers.extend import Extend
from assistant4discord.nlp_tasks.find_times import timestamp_to_local


class Note(Extend):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        noted: str
            User's message used as note string.

        """
        super().__init__(**kwargs)
        self.name = "note_it"
        self.noted = ""

    def doit(self):
        self.noted = self.get_message()

    def __str__(self):
        return "noted on {}\n{}".format(timestamp_to_local(self.created_on), self.noted)
