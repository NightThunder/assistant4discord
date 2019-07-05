import asyncio
from assistant4discord.assistant.commands.timer_helper.timer_class import Timer
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class TimeIt(AddItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'time'
        self.help = '```***Timer help***\n' \
                    'Run a command in specified time.\n' \
                    'Example: time <time when to run> <any command>```'
        self.time_coro = True

    async def coro_doit(self, timer):

        await self.message.channel.send(str(timer))

        while True:
            await asyncio.sleep(timer.time_to_timer)
            await timer.future_command.doit()

            if timer.every is False:
                return

    async def AddItem_doit(self, item_obj=None):

        timer = Timer(message=self.message, similarity=self.sim, commands=self.commands, command_vectors=self.command_vectors, calls=self.calls)

        if timer.time_to_timer and timer.future_command:
            task = self.client.loop.create_task(self.coro_doit(timer))
            timer.task = task
            self.all_items.append(timer)
        else:
            await self.message.channel.send('something went wrong')

    async def doit(self):
        await self.AddItem_doit()


class ShowTimers(ShowItems):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = ' '
        self.call = 'show timer'

    async def doit(self):
        await self.ShowItems_doit('TimeIt')


class RemoveTimer(RemoveItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = ' '
        self.call = 'remove timer'

    async def doit(self):
        await self.RemoveItem_doit('TimeIt')
