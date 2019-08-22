from .extensions.reminder_ext import Reminder
from .helpers.tui import ShowItems, RemoveItem
from .helpers.mongodb_adder import AddItem


class RemindMe(AddItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemindMe help***\n"
            "Set user's previous message as reminder text.\n"
            "Call: reminder\n"
            "Example: reminder <number> <time word>\n"
            "Valid times: second, minute, hour, day, week, name of days, time in format at h:m:s dates in format on d/m/y.\n"
            "Warning: at and on MUST be used with times and dates.\n```"
        )
        self.call = "reminder stevilka"

    async def doit(self):
        await self.AddItem_doit(Reminder)


class ShowReminders(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***ShowReminders help***\n"
            "Display user's active reminders.\n"
            "Call: show reminders\n```"
        )
        self.call = "show reminders"

    async def doit(self):
        await self.ShowItems_doit(Reminder)


class RemoveReminder(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveReminder help***\n"
            "Cancels user's active reminder.\n"
            "Call: remove reminder <number>\n"
            "Example: cancel reminder <reminder's number shown in ShowReminders>```"
        )
        self.call = "remove reminder stevilka"

    async def doit(self):
        await self.RemoveItem_doit(Reminder)
