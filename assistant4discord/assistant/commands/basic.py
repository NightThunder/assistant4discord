import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.remind_me.reminder import Reminder


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


class RemindMe(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'reminder'
        self.help = 'Sets reminder. Note: works with keyword "reminder" followed by time parameters.'
        self.all_reminders = []

    async def coro_doit(self, reminder):

        await self.message.channel.send('{}'.format(reminder.reminder_str))

        while True:
            await asyncio.sleep(reminder.time_to_message)
            await self.message.channel.send(reminder.to_remind)

            if reminder.every is False:
                break

    async def doit(self):

        reminder = Reminder(self.client, self.message)

        if reminder.time_to_message and reminder.to_remind:
            # task = asyncio.ensure_future(self.coro_doit(reminder))
            task = self.client.loop.create_task(self.coro_doit(reminder))
            reminder.task = task
            self.all_reminders.append(reminder)
        else:
            await self.message.channel.send('something went wrong')

# TODO write cancel reminder
