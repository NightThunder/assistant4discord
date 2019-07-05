from assistant4discord.assistant.commands.reminder_helper.reminder_class import Reminder
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class RemindMe(AddItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = ' '
        self.call = 'reminder'
        self.time_coro = True

    async def doit(self):
        await self.AddItem_doit(Reminder)


class ShowReminders(ShowItems):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = ' '
        self.call = 'show reminder'

    async def doit(self):
        await self.ShowItems_doit('RemindMe')


class RemoveReminder(RemoveItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = ' '
        self.call = 'remove reminder'

    async def doit(self):
        await self.RemoveItem_doit('RemindMe')
