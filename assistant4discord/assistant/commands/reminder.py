import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.reminder_helper.reminder_class import Reminder


class RemindMe(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'reminder'
        self.help = '```***RemindMe help***\n' \
                    'Set user\'s previous message as reminder text.\n' \
                    'Use: reminder <number1> <time1> <number2> <time2> ...\n' \
                    'Valid times: second, sec, s, minute, min, m, hour, h, day, d, week, w\n' \
                    'Notes: use with ShowReminders and KillReminder```'
        self.all_reminders = []

    def remove_dead_reminders(self):

        all_active_reminders = []

        for reminder in self.all_reminders:
            if not reminder.task.done():
                all_active_reminders.append(reminder)

        self.all_reminders = all_active_reminders

    async def coro_doit(self, reminder):

        await self.message.channel.send('reminder: {}'.format(str(reminder)))

        while True:
            await asyncio.sleep(reminder.time_to_message)
            await self.message.channel.send(reminder.to_remind)

            if reminder.every is False:
                return

    async def doit(self):
        reminder = Reminder(client=self.client, message=self.message)

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
        self.help = '```***ShowReminders help***\n' \
                    'Display user\'s active reminders.\n' \
                    'Example: see reminder | show reminder | get reminder etc.```'

    async def doit(self):

        self.commands['RemindMe'].remove_dead_reminders()

        all_reminders = self.commands['RemindMe'].all_reminders
        reminder_str = ''
        n_reminders = 0
        for i, reminder in enumerate(all_reminders):
            if reminder.message.author == self.message.author and not reminder.task.done():
                reminder_str += '**reminder {}:** {}\n'.format(i, str(reminder))

                if i != len(all_reminders) - 1:
                    reminder_str += '--------------------\n'

                n_reminders += 1

        if n_reminders != 0:
            await self.message.channel.send(reminder_str)
        else:
            await self.message.channel.send('You have no active reminders!')


class KillReminder(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'kill reminder'
        self.help = '```***KillReminder help***\n' \
                    'Cancels user\'s active reminder.\n' \
                    'Example: cancel reminder <reminder\'s number shown in ShowReminders>```'

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

# Solution with TimeIt:
# problem1: reminder list and timer list together
# problem2: cant see reminder description in show timer
# class RemindMe(Master):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.call = 'reminder stevilka time'
#         self.help = '```***RemindMe help***\n' \
#                     'Set user\'s previous message as reminder text.\n' \
#                     'Use: reminder <number1> <time1> <number2> <time2> ...\n' \
#                     'Valid times: second, sec, s, minute, min, m, hour, h, day, d, week, w```'
#
#     def get_message(self):
#
#         count = 0
#         for msg in reversed(self.client.cached_messages):
#             if msg.author == self.message.author:
#                 count += 1
#
#             if count == 2:
#                 to_remind = '<@{}> {}'.format(self.message.author.id, msg.content)
#                 return to_remind
#
#         return None
#
#     async def doit(self):
#         to_remind = self.get_message()
#
#         if to_remind:
#             await self.message.channel.send(to_remind)
#         else:
#             await self.message.channel.send('something went wrong')
