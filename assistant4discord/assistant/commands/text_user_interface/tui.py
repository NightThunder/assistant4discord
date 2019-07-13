import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
import inspect


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

    @staticmethod
    def obj_error_check(obj):
        """ Check if any attribute None.

        Args:
            obj: Item

        Returns: True if found None else False
        """
        master_attr = vars(Master())

        for attr, value in vars(obj).items():
            if attr not in master_attr and value is None:
                return True

        return False

    async def coro_doit(self, item_obj, is_to_do_async):
        """  loop.create_task function.

        Args:
            item_obj: helper object
            is_to_do_async: True if to_do a coroutine
        """
        while True:

            await asyncio.sleep(item_obj.time_to_message)

            if is_to_do_async:                                            # check if to_do is async def
                discord_send = await item_obj.to_do()
            else:
                discord_send = item_obj.to_do()                           # run to_do method

            if len(discord_send) == 0:                                    # check if something in message
                pass
            else:                                                         # just in case len() > 2000 (max message length for discord)
                for i in range(int(len(discord_send) / 2000) + 1):
                    await self.message.channel.send(discord_send[i * 2000:(i + 1) * 2000])

            if item_obj.every is False:                                   # if every is false we are done else we loop
                return

    async def AddItem_doit(self, item_obj):
        """ Adds item to all_items. If coroutine creates task and adds it to event loop.

        Args:
            item_obj: helper object
        """
        Item = item_obj(client=self.client, message=self.message)       # initialize helper object

        is_to_do_async = inspect.iscoroutinefunction(item_obj.to_do)    # check if helper to_do method a coroutine

        if getattr(Item, 'run_on_init', False):                         # run on initialization if True
            if is_to_do_async:
                await Item.to_do()
            else:
                Item.to_do()

        if self.obj_error_check(Item):                                  # check if all helper attributes not None
            await self.message.channel.send('something went wrong')
        else:
            if self.time_coro:                                          # check if helper uses asyncio.sleep
                await self.message.channel.send(str(Item))

                task = self.client.loop.create_task(self.coro_doit(Item, is_to_do_async))     # add coro_doit to event loop
                setattr(Item, 'task', task)                             # save task as attribute of Item
                self.all_items.append(Item)                             # save Item to list
            else:
                self.all_items.append(Item)                             # save Item to list if helper does not use asyncio
                await self.message.channel.send(str(Item))


class ShowItems(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def ShowItems_doit(self, item_obj_str):

        all_items = self.commands[item_obj_str].all_items

        for item in all_items.copy():
            if item.task.done():
                all_items.remove(item)

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
            await self.message.channel.send('something went wrong')


class RemoveItem(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def RemoveItem_doit(self, item_obj_str):

        all_items = self.commands[item_obj_str].all_items

        for item in all_items.copy():
            if item.task.done():
                all_items.remove(item)

        try:
            to_kill = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong')
            return

        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author and i == to_kill:

                if self.commands[item_obj_str].time_coro:
                    item.task.cancel()
                else:
                    all_items.pop(i)

                break
            else:
                n_items += 1

        if to_kill > n_items:
            await self.message.channel.send('something went wrong')
        else:
            await self.message.channel.send('item {} removed!'.format(to_kill))
