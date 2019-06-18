from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
import datetime
import time


times = {'second': 1, 'seconds': 1, 'sec': 1, 's': 1, 'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
         'hour': 3600, 'hours': 3600, 'h': 3600, 'day': 86400, 'days': 86400, 'd': 86400, 'week': 604800,
         'weeks': 604800, 'w': 604800}


class Reminder(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_remind = self.get_message()
        self.time_to_message = self.time_message()
        self.every = self.every_t()
        self.reminder_str = '{}\nset for: {}'.format(self.to_remind[22:], datetime.datetime.fromtimestamp(int(time.time() + self.time_to_message)).strftime('%d/%m/%Y @ %H:%M:%S'))
        self.task = None

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
        message = word2vec_input(self.message.content[22:], replace_num=False)

        time_to_message = 0
        for i, word in enumerate(message):
            if word in times:
                try:
                    time_to_message += times[word] * int(message[i-1])
                except ValueError:
                    return None

        return time_to_message

    def every_t(self):
        message = word2vec_input(self.message.content[22:], replace_num=False)
        if 'every' in message:
            return True
        else:
            return False
