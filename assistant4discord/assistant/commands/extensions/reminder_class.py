import time
from assistant4discord.nlp_tasks.find_times import timestamp_to_local, convert_sec
from assistant4discord.assistant.commands.helpers.extend import Extend


class Reminder(Extend):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        to_remind: str
            User's message used as reminder string.

        """
        super().__init__(**kwargs)
        self.name = "remind_me"
        self.use_asyncio = True
        self.to_remind = ""

    def doit(self):
        if self.switch == 0:
            (self.time_to_message, self.every) = self.time_message()

            self.to_remind = "<@{}> {}".format(self.message.author.id, self.get_message())
            self.switch += 1
            return self.to_remind
        else:
            self.created_on = int(time.time())
            return self.to_remind

    def __str__(self):
        if self.every:
            return "reminder: {}\nset every {}\nnext reminder on {}".format(
                self.to_remind[22:],
                convert_sec(self.every),
                timestamp_to_local(self.time_to_message + self.created_on),
            )
        else:
            return "reminder: {}\nset for: {}".format(
                self.to_remind[22:],
                timestamp_to_local(self.time_to_message + self.created_on),
            )
