import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master


class AddItem(Master):
    """
        idea: each command (non basic commands) has it's own helper class that stores all the data and instructions how
              to execute that command (every command that is ran from discord is represented by an object).
              Saving these objects and using them later is a very common task. AddItem is meant to simplify this process.
              AddItem initializes given object with client and message from discord and saves it to a list. If self.time_coro == True
              (command attribute) it will run that object in a given time if self.every == False it gets removed from list after it ran.
              If self.time_coro == False it simply saves object to a list to be accessed later. Objects can be accessed from all_items list
              with ShowItems or RemoveItems.

        Example: see reminder.py and reminder_class.py

        Notes: inheritance: Command -> tui.py helper classes -> Master (is set in messenger)

        self.all_items: list of all items (self.item objects)
        self.time_coro: if self.item uses asyncio.sleep()
        self.send_str: send this to discord
        self.item: helper object

        item_obj => helper (obj): all helpers must have __str__ and to_do() method. If time_coro must have self.time_to_message and self.every
        helper example: reminder_class.Reminder (contains all relevant information for reminder command such as: how to get reminder and time to reminder)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_items = []
        self.time_coro = False

    def remove_dead_items(self):
        """ Removes all finished coroutines (tasks) from all_items."""
        all_active_items = []

        for item in self.all_items:
            if not item.task.done():
                all_active_items.append(item)

        self.all_items = all_active_items

    async def coro_doit(self, item_obj):
        """  loop.create_task function.

        Args:
            item_obj: helper object
        """
        while True:
            await asyncio.sleep(item_obj.time_to_message)

            discord_send = await item_obj.to_do()        # to_do() string output

            if len(discord_send) == 0:      # check if something in message
                pass
            else:
                for i in range(int(len(discord_send) / 2000) + 1):        # just in case len() > 2000 (max message length for discord)
                    await self.message.channel.send(discord_send[i * 2000:(i + 1) * 2000])

            if item_obj.every is False:        # if every is false we are done else we loop
                return

    async def AddItem_doit(self, item_obj):
        """ Adds item to all_items. If coroutine creates task and adds it to event loop.

        Args:
            item_obj: helper object
        """
        Item = item_obj(client=self.client, message=self.message)

        if self.time_coro:

            if Item.time_to_message and await Item.to_do() is not None:       # <- watch Item.to_do()
                await self.message.channel.send(str(Item))

                task = self.client.loop.create_task(self.coro_doit(Item))
                setattr(Item, 'task', task)
                self.all_items.append(Item)
            else:
                await self.message.channel.send('something went wrong in tui.py line 71')

        else:
            if Item.to_do() is not None:
                self.all_items.append(Item)
                await self.message.channel.send(str(Item))
            else:
                await self.message.channel.send('something went wrong in tui.py line 78')


class ShowItems(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def ShowItems_doit(self, item_obj_str):

        add_items_obj = self.commands[item_obj_str]
        all_items = add_items_obj.all_items

        if add_items_obj.time_coro:
            add_items_obj.remove_dead_items()

        item_str = ''
        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author:
                item_str += '**{}:** {}\n'.format(i, str(item))

                if i != len(all_items) - 1:
                    item_str += '--------------------\n'

                n_items += 1

        if n_items != 0:
            await self.message.channel.send(item_str)
        else:
            await self.message.channel.send('something went wrong in tui.py line 108')


class RemoveItem(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def RemoveItem_doit(self, item_obj_str):

        add_items_obj = self.commands[item_obj_str]
        all_items = add_items_obj.all_items

        if add_items_obj.time_coro:
            add_items_obj.remove_dead_items()

        try:
            to_kill = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong in tui.py line 127')
            return

        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author and i == to_kill:

                if add_items_obj.time_coro:
                    item.task.cancel()
                else:
                    all_items.pop(i)

                break
            else:
                n_items += 1

        if to_kill > n_items:
            await self.message.channel.send('something went wrong in tui.py line 144')
        else:
            await self.message.channel.send('item {} removed!'.format(to_kill))
