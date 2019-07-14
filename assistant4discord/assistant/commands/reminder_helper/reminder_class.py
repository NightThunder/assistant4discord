from assistant4discord.assistant.commands.master.master_class import Master
import time
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc


class Reminder(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_on_init = True
        (self.time_to_message, self.every) = self.time_message()
        self.n = 0
        self.to_remind = ''
        self.created_on = time.time()

    def to_do(self):
        if self.n == 0:
            self.to_remind = self.get_message()
            self.n += 1
            return self.to_remind
        else:
            return self.to_remind

    def get_message(self):
        """ Message to be set for reminder.

        Returns: @author author's last message in chat
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

        Returns: seconds to message
        """
        time_to_command, every = sent_time_finder(self.message.content)

        return time_to_command, every

    def __str__(self):
        if self.every:
            return '{}\nset every: {}'.format(self.to_remind[22:], timestamp_to_utc(int(self.time_to_message + self.created_on)))
        else:
            return '{}\nset for: {}'.format(self.to_remind[22:], timestamp_to_utc(int(self.time_to_message + self.created_on)))
