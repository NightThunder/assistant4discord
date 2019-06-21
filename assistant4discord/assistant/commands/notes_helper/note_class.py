from assistant4discord.assistant.commands.master.master_class import Master
import datetime
import time


class Note(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note = self.get_note()
        self.note_time = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y @ %H:%M:%S')

    def get_note(self):

        c = 0
        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                return msg.content

        return None

    def __str__(self):
        return '{}\n{}'.format(self.note_time, self.note)
