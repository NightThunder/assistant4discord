import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.reminder_helper.reminder_class import Reminder


class RemindMe(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'reminder stevilka time'
        self.help = 'Sets reminder. Note: works with keyword "reminder" followed by time parameters.'
        self.all_reminders = []

    def remove_dead_reminders(self):

        all_active_reminders = []

        for reminder in self.all_reminders:
            if not reminder.task.done():
                all_active_reminders.append(reminder)

        self.all_reminders = all_active_reminders

    async def coro_doit(self, reminder):

        await self.message.channel.send('reminder: {}'.format(reminder.reminder_str))

        while True:
            await asyncio.sleep(reminder.time_to_message)
            await self.message.channel.send(reminder.to_remind)

            if reminder.every is False:
                break

    async def doit(self):
        reminder = Reminder(self.client, self.message)

        if reminder.time_to_message and reminder.to_remind:

            task = self.client.loop.create_task(self.coro_doit(reminder))
            reminder.task = task

            self.all_reminders.append(reminder)
        else:
            await self.message.channel.send('something went wrong')


class ShowReminders(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'show reminder'
        self.help = 'Shows all active reminders.'

    async def doit(self):

        self.commands['RemindMe'].remove_dead_reminders()

        reminder_str = ''

        n_reminders = 0
        for i, reminder in enumerate(self.commands['RemindMe'].all_reminders):
            if reminder.message.author == self.message.author and not reminder.task.done():
                reminder_str += 'reminder {}: {}\n'.format(i, reminder.reminder_str)
                n_reminders += 1

        if n_reminders != 0:
            await self.message.channel.send(reminder_str)
        else:
            await self.message.channel.send('You have no active reminders!')


class KillReminder(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'kill reminder stevilka'
        self.help = 'Cancels active reminder.'

    async def doit(self):

        self.commands['RemindMe'].remove_dead_reminders()

        try:
            to_kill = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong')
            return

        n_reminders = 0
        for i, reminder in enumerate(self.commands['RemindMe'].all_reminders):
            if reminder.message.author == self.message.author and not reminder.task.done() and i == to_kill:
                reminder.task.cancel()
                break
            else:
                n_reminders += 1

        if to_kill > n_reminders:
            await self.message.channel.send('Could not find that reminder!')
        else:
            await self.message.channel.send('Reminder {} canceled!'.format(to_kill))
