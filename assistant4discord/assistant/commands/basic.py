import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import datetime
import time


class Master:

    def __init__(self, client=None, message=None, similarity=None):
        """ Base class for commands.

        Args:
            client: discord client object
            message: discord message object
            similarity: Similarity object from assistant4discord.nlp_tasks.similarity
        """
        self.client = client
        self.message = message
        self.sim = similarity


class Help(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'help'
        self.commands = None

    async def doit(self):

        message = self.message.content[22:]

        if len(word2vec_input(message)) > 1:
            for i, (command_str, command) in enumerate(self.commands.items()):
                if command_str in message.lower() and command_str != 'help':
                    await self.message.channel.send(command.help)
                    break

                if i == len(self.commands) - 1:
                    await self.message.channel.send('Command not found!')

        else:
            command_str = 'My commands: '
            for i, command_str_ in enumerate(self.commands.keys()):
                if i < len(self.commands) - 1:
                    command_str += command_str_.lower() + ', '
                else:
                    command_str += command_str_.lower()

            command_str += '\nType help <command> for more info!'

            await self.message.channel.send(command_str)


class Ping(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'ping'
        self.help = 'Ping discord server and return response time in ms.'

    async def doit(self):
        await self.message.channel.send('{} ms'.format(round(self.client.latency * 1000)))


class Reminder(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'reminder'
        self.help = 'Sets reminder. Note: works with keyword "reminder" followed by time parameters.'
        self.times = {'second': 1, 'seconds': 1, 'sec': 1, 's': 1, 'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
                      'hour': 3600, 'hours': 3600, 'h': 3600, 'day': 86400, 'days': 86400, 'd': 86400, 'week': 604800,
                      'weeks': 604800, 'w': 604800}

    def get_message(self):
        c = 0

        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                to_remind = '<@{}> {}'.format(self.message.author.id, msg.content)
                return to_remind

        return None

    def time_message(self):
        message = word2vec_input(self.message.content[22:], replace_num=False)

        time_to_message = 0
        for i, word in enumerate(message):
            if word in self.times:
                try:
                    time_to_message += self.times[word] * int(message[i-1])
                except ValueError:
                    return None

        return time_to_message

    async def doit(self):
        message = word2vec_input(self.message.content[22:], replace_num=False)

        to_remind = self.get_message()

        if not to_remind:
            await self.message.channel.send('something went wrong')
        else:
            time_to_message = self.time_message()

            if not time_to_message:
                await self.message.channel.send('something went wrong')
            else:
                my_time = datetime.datetime.fromtimestamp(int(time.time() + time_to_message)).strftime('%d/%m/%Y @ %H:%M:%S')
                await self.message.channel.send('reminder set for: {}'.format(my_time))

                while True:
                    await asyncio.sleep(time_to_message)
                    await self.message.channel.send(to_remind)

                    if 'every' not in message:
                        break

# TODO cancel reminders
