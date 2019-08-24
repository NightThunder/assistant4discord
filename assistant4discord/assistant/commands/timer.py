from .extensions.timer_ext import Timer
from .helpers.tui import ShowItems, RemoveItem
from .helpers.mongodb_adder import AddItem


class TimeIt(AddItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***Timer help***\n"
            "Set a timer for any command.\n"
            "Call: time ...\n"
            "Note: command is ran when timer is finished.\n"
            "Example: time <time when to run> <any command>\n"
            "Valid times: second, minute, hour, day, week, name of days, time in format at h:m:s dates in format on d/m/y.\n"
            "Warning: at and on MUST be used with times and dates.\n```"
        )
        self.call = "time stevilka"

    async def doit(self):
        await self.AddItem_doit(Timer(client=self.client, message=self.message, similarity=self.sim, commands=self.commands))


class ShowTimers(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = "```***ShowTimers help***\n" "Display user's active timers.\n```"
        self.call = "show timers"

    async def doit(self):
        await self.ShowItems_doit(Timer)


class RemoveTimer(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveTimer help***\n"
            "Cancels user's active timer.\n"
            "Example: cancel timer <timer's number shown in ShowTimers>```"
        )
        self.call = "remove timer stevilka"

    async def doit(self):
        await self.RemoveItem_doit(Timer)
