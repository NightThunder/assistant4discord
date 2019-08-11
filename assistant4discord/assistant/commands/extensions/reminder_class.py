from assistant4discord.assistant.commands.master.master_class import Master
import time
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_local, convert_sec


class Reminder(Master):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        name: str
            Used for identification.
        run_on_init: bool
            If True runs once on initialization.
        use_asyncio: bool
            True because asyncio is needed.
        time_to_message: int
            Seconds to message.
        every: bool
            True if repeated (do again after sleep).
        switch: int
            0 if never ran, 1 if ran once or more.
        to_remind: str
            User's message used as reminder string.
        created_on: int
            When did doit() ran.

        Note
        ----
        All None attributes in __init__ are initialized in doit() method.

        """
        super().__init__(**kwargs)
        self.name = "remind_me"
        self.run_on_init = True
        self.use_asyncio = True
        self.time_to_message = None
        self.every = None
        self.switch = 0
        self.to_remind = ""
        self.created_on = int(time.time())

    def doit(self):
        if self.switch == 0:
            (self.time_to_message, self.every) = self.time_message()

            self.to_remind = self.get_message()
            self.switch += 1
            return self.to_remind
        else:
            self.created_on = int(time.time())
            return self.to_remind

    def get_message(self):
        """ Get message from discord.

        Loop over all messages (newest to oldest) and find author's second message (first is this command).

        Returns
        -------
        str
            @author <author's last message in chat>

        """
        c = 0

        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                to_remind = "<@{}> {}".format(self.message.author.id, msg.content)
                return to_remind

        return None

    def time_message(self):
        time_to_command, every = sent_time_finder(self.message.content)
        return time_to_command, every

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
