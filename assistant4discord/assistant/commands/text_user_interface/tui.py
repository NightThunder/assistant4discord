import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
import inspect


class AddItem(Master):
    """ Command memory.

    Inherit this class in your command if you need to save an object that represents a command.

    Types of commands:
        (i) normal command (static)
            Doesn't use any asyncio. AddItem saves it to a list. Remains in list until owner removes it.
        (ii) async command
            use_asyncio = True
            Uses asyncio, aiohttp, ... . AddItem saves it to a list and initializes a timer. Removed when timer is up.
            Can also be removed by user.

    Code example
    ------------

    reminder.py:
    Callable command from discord.

    class RemindMe(AddItem):        # inherits from this class
        def __init__(self):
        ...
        self.use_asyncio = True     # tells AddItem that Reminder is asynchronous

        async def doit(self):
            await self.AddItem_doit(Reminder)       # pass Reminder (actual command) to doit from AddItem


    reminder_class.py:
    Actual command.

    class Reminder(Master):    # inherit from Master (same as basic commands)

    def __init__(self, **kwargs):                                   # **kwargs needed for initialization in AddItem
        super().__init__(**kwargs)
        self.run_on_init = True                                     # runs to_do once on initialization
        (self.time_to_message, self.every) = self.time_message()    # get time to message and every (this is why use_asyncio is needed)
        self.n = 0                                                  # dummy variable that tells the class it ran more then once
        self.to_remind = ''                                         # reminder string (user's last message)
        self.created_on = time.time()                               # time when initialized

    def to_do(self):                                    # Actual to_do, this gets ran by AddItem (can be async)
        if self.n == 0:                                 # check if first run (important because of every)
            self.to_remind = self.get_message()         # get reminder string
            self.n += 1
            return self.to_remind                       # returns reminder string to AddItem
        else:
            return self.to_remind

    def get_message(self):
        ...

    def time_message(self):
        ...

    def __str__(self):    # every 'helper' object must have __str__ that tells AddItem how to display this object
        ...


    Discord example
    ---------------

    me: remind me this
    me: @assistant reminder tomorrow
    assistant: remind me this                           # reminder string
               set for: 24.07.2019 @ 20:53:15           # reminder in 24h from now

    me: @assistant show reminders
    assistant: 0 - remind me this
               set for: 24.07.2019 @ 20:53:15

    me: @assistant remove reminder 0
    assistant: item 0 removed!                          # timer canceled, reminder removed from list
    """

    def __init__(self):
        """
        Other Parameters
        ----------------
        all_items: list of obj
            List of command objects.
        use_asyncio: bool
            Default value.
        """
        super().__init__()
        self.all_items = []
        self.use_asyncio = False

    @staticmethod
    def obj_error_check(obj):
        """ Check if any attribute None.

        Parameters
        ----------
        obj: obj
            Command object.

        Returns
        -------
        bool
            True if found None else False
        """
        master_attr = vars(Master())

        for attr, value in vars(obj).items():
            if attr not in master_attr and value is None:
                return True

        return False

    async def coro_doit(self, item_obj, is_to_do_async):
        """ loop.create_task function.

        Parameters
        ----------
        item_obj: obj
            Command object
        is_to_do_async: bool
            True if to_do a coroutine.
        """
        while True:

            await asyncio.sleep(item_obj.time_to_message)

            # check if to_do is async def
            if is_to_do_async:
                discord_send = await item_obj.to_do()
            else:
                discord_send = item_obj.to_do()

            # check if something in message
            # just in case len() > 2000 (max message length for discord)
            if len(discord_send) == 0:
                pass
            else:
                for i in range(int(len(discord_send) / 2000) + 1):
                    await self.message.channel.send(discord_send[i * 2000: (i + 1) * 2000])

            # if every is false we are done else we loop
            if item_obj.every is False:
                return

    async def AddItem_doit(self, item_obj):
        """ Adds item to all_items. If use_asyncio create task and add it to event loop.

        Parameters
        ----------
        item_obj: obj
            Command object
        """

        # initialize helper object
        Item = item_obj(client=self.client, message=self.message)

        # check if helper to_do method a coroutine
        is_to_do_async = inspect.iscoroutinefunction(item_obj.to_do)

        # run on initialization if True
        if Item.run_on_init:
            if is_to_do_async:
                await Item.to_do()
            else:
                Item.to_do()

        # check if all helper attributes not None
        if self.obj_error_check(Item):
            await self.message.channel.send("something went wrong")
        else:
            if self.use_asyncio:                                                             # check if helper uses asyncio
                await self.message.channel.send(str(Item))

                task = self.client.loop.create_task(self.coro_doit(Item, is_to_do_async))    # add coro_doit to event loop
                setattr(Item, "task", task)    # save task as attribute of Item
                self.all_items.append(Item)    # save Item to list
            else:
                self.all_items.append(Item)    # save Item to list if helper doesn't use asyncio
                await self.message.channel.send(str(Item))


class ShowItems(Master):
    """ Display all_items.

    Makes a nice text menu in discord
    """

    def __init__(self):
        super().__init__()

    async def ShowItems_doit(self, item_obj_str, public=False):
        """
        Parameters
        ----------
        item_obj_str: str
            Command name which inherits from AddItem.

        public: bool
            If True show items for this command public (means that everyone can call <show command> and see a list).

        Note
        ----
        Uses self.commands to get to command object and get its all_items.
        """

        # access global commands
        add_item_ref = self.commands[item_obj_str]
        all_items = add_item_ref.all_items

        # check if command uses asyncio
        if add_item_ref.use_asyncio:
            for item in all_items.copy():
                if item.task.done():
                    all_items.remove(item)

        item_str = ""
        n_items = 0

        if public:
            for i, item in enumerate(all_items):
                item_str += "**{}** - {}\n".format(i, str(item))

                if i != len(all_items) - 1:
                    item_str += "--------------------\n"

                n_items += 1
        else:
            for i, item in enumerate(all_items):
                if item.message.author == self.message.author:
                    item_str += "**{}** - {}\n".format(i, str(item))

                    if i != len(all_items) - 1:
                        item_str += "--------------------\n"

                    n_items += 1

        if n_items != 0:
            await self.message.channel.send(item_str)
        else:
            await self.message.channel.send("something went wrong")


class RemoveItem(Master):
    """ Remove from all_items."""

    def __init__(self):
        """ Same as ShowItems.

        Note
        ----
        Doesn't have public attribute. Items can only be removed by owner.
        """
        super().__init__()

    async def RemoveItem_doit(self, item_obj_str):

        add_item_ref = self.commands[item_obj_str]
        all_items = add_item_ref.all_items

        if add_item_ref.use_asyncio:
            for item in all_items.copy():
                if item.task.done():
                    all_items.remove(item)

        try:
            to_kill = int(word2vec_input(self.message.content, replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send("something went wrong")
            return

        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author and i == to_kill:

                if add_item_ref.use_asyncio:
                    item.task.cancel()
                else:
                    all_items.pop(i)

                break
            else:
                n_items += 1

        if to_kill > n_items:
            await self.message.channel.send("something went wrong")
        else:
            await self.message.channel.send("item {} removed!".format(to_kill))
