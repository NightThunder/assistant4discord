from assistant4discord.assistant.commands.master.master_class import Master
import time
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc


class Reminder(Master):

    def __init__(self, **kwargs):
        """ See tui.py"""

        super().__init__(**kwargs)
        self.name = 'reminders'
        self.run_on_init = True
        self.use_asyncio = True
        self.time_to_message = None
        self.every = None
        self.n = 0
        self.to_remind = ''
        self.created_on = int(time.time())

    def todo(self):
        if self.n == 0:
            (self.time_to_message, self.every) = self.time_message()

            self.to_remind = self.get_message()
            self.n += 1
            return self.to_remind
        else:
            self.created_on = int(time.time())
            return self.to_remind

    def get_message(self):
        """ Message to be set for reminder.

        Loop over all messages (newest to oldest) and find author's second message (first is this command).
        Set this message as reminder.

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
                to_remind = '<@{}> {}'.format(self.message.author.id, msg.content)
                return to_remind

        return None

    def time_message(self):
        """ Parses message for time words.

        Return
        ------
        (int, bool)
        """
        time_to_command, every = sent_time_finder(self.message.content)

        return time_to_command, every

    def __str__(self):
        if self.every:
            return '{}\nset every: {}'.format(self.to_remind[22:], timestamp_to_utc(self.time_to_message + self.created_on))
        else:
            return '{}\nset for: {}'.format(self.to_remind[22:], timestamp_to_utc(self.time_to_message + self.created_on))
