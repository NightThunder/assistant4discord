import asyncio
import time
from .extensions.timer_class import Timer
from .extensions.helpers.tui import ShowItems, RemoveItem
from .extensions.helpers.mongodb_adder import AddItem, Obj2Dict


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
            "Warning: at and on MUST be used with times and dates.\n"
            "Warning: RESETS ON SERVER RESTART!```"
        )
        self.call = "time stevilka"

    async def coro_doit(self, item_obj):
        """ loop.create_task function.

        Parameters
        ----------
        item_obj: obj
            Command object
        """
        make_db_entry = True

        while True:

            if not item_obj.future_command_call:
                return None

            if make_db_entry:
                res = await Obj2Dict(item_obj).make_doc(self.db)
                doc_id = res.inserted_id
                make_db_entry = False

            elif not await self.find_doc(doc_id):
                return

            else:
                for command_obj in self.commands.values():
                    if command_obj.call == item_obj.future_command_call:
                        command_obj.message = self.message
                        command = command_obj

                await asyncio.sleep(item_obj.time_to_message)
                await command.doit()

                if item_obj.every is False:
                    await self.delete_doc(doc_id)
                    return
                else:
                    item_obj.created_on = int(time.time())
                    await Obj2Dict(item_obj).update_doc(self.db, doc_id)

    async def doit(self):
        await self.AddItem_doit(Timer(message=self.message, similarity=self.sim, commands=self.commands))


class ShowTimers(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = "```***ShowTimers help***\n" "Display user's active timers.\n```"
        self.call = "show timers"

    async def doit(self):
        await self.ShowItems_doit("TimeIt")


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
        await self.RemoveItem_doit("TimeIt")
