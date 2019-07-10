from assistant4discord.assistant.commands.reminder_helper.reminder_class import Reminder
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class RemindMe(AddItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***RemindMe help***\n' \
                    'Set user\'s previous message as reminder text.\n' \
                    'Use: reminder <number1> <time1> <number2> <time2> ...\n' \
                    'Valid times: see timer help\n```'
        self.call = 'reminder stevilka'
        self.time_coro = True

    async def doit(self):
        await self.AddItem_doit(Reminder)


class ShowReminders(ShowItems):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***ShowReminders help***\n' \
                    'Display user\'s active reminders.\n' \
                    'Example: see reminder | show reminder | get reminder etc.```'
        self.call = 'show reminders'

    async def doit(self):
        await self.ShowItems_doit('RemindMe')


class RemoveReminder(RemoveItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***RemoveReminder help***\n' \
                    'Cancels user\'s active reminder.\n' \
                    'Example: cancel reminder <reminder\'s number shown in ShowReminders>```'
        self.call = 'remove reminder stevilka'

    async def doit(self):
        await self.RemoveItem_doit('RemindMe')
