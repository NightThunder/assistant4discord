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
        self.name = None
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

    async def delete_finished(self, collection_name, _id):
        await self.db[collection_name].delete_one({'_id': _id})

    async def verify_doc(self, collection_name, _id):
        found = await self.db[collection_name].find_one({'_id': _id})

        if found:
            return True
        else:
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
        make_db_entry = True

        while True:

            if make_db_entry:
                res = await Obj2Dict(item_obj).make_document(self.db)
                doc_id = res.inserted_id
                make_db_entry = False

            elif not await self.verify_doc(self.name, doc_id):
                return

            else:
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
                    await self.delete_finished(self.name, doc_id)
                    return

    async def AddItem_doit(self, item_obj):
        """ Adds item to all_items. If use_asyncio create task and add it to event loop.

        Parameters
        ----------
        item_obj: obj
            Command object
        """

        # initialize helper object
        if '__module__' in vars(item_obj):
            Item = item_obj(client=self.client, message=self.message)
        else:
            Item = item_obj

        self.name = Item.name

        # check if helper to_do method a coroutine
        is_to_do_async = inspect.iscoroutinefunction(item_obj.to_do)

        # run on initialization if True
        if getattr(Item, 'run_on_init', False):
            if is_to_do_async:
                await Item.to_do()
            else:
                Item.to_do()

        # check if all helper attributes not None
        if self.obj_error_check(Item):
            try:
                await self.message.channel.send("something went wrong")
            except AttributeError:
                pass
        else:
            if self.use_asyncio:                                                             # check if helper uses asyncio
                await self.message.channel.send(str(Item))
                task = self.client.loop.create_task(self.coro_doit(Item, is_to_do_async))    # add coro_doit to event loop
                if not task:
                    await self.message.channel.send("something went wrong")
            else:
                await Obj2Dict(Item).make_document(self.db)
                await self.message.channel.send(str(Item))


class ShowItems(Master):
    """ Display all_items.

    Makes a nice text menu in discord
    """

    def __init__(self):
        super().__init__()

    async def get_all_docs(self, collection_name):
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def get_user_docs(self, collection_name, author):
        cursor = self.db[collection_name].find({'username': author})
        return await cursor.to_list(length=None)

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

        item_name = self.commands[item_obj_str].name

        if not item_name:
            await self.message.channel.send("something went wrong")
            return

        item_str = ""
        n_items = 0

        if public:
            all_items = await self.get_all_docs(item_name)

            for i, item in enumerate(all_items):
                try:
                    item_str += "**{}** - {} by {}".format(i, item['text'], item['username'])
                except KeyError:
                    item_str += "**{}** - {}".format(i, item['text'])

                item_str += "\n-----------------------------------\n"
                n_items += 1

        else:
            user_items = await self.get_user_docs(item_name, str(self.message.author))

            for i, item in enumerate(user_items):
                if str(self.message.author) == item['username']:
                    item_str += "**{}** - {}".format(i, item['text'])
                    item_str += "\n-----------------------------------\n"
                    n_items += 1

        item_str = item_str[:-37]

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

    async def get_user_docs(self, collection_name, author):
        cursor = self.db[collection_name].find({'username': author})
        return await cursor.to_list(length=None)

    async def delete_doc(self, collection_name, _id):
        await self.db[collection_name].delete_one({'_id': _id})

    async def RemoveItem_doit(self, item_obj_str):

        item_name = self.commands[item_obj_str].name

        if not item_name:
            await self.message.channel.send("something went wrong")
            return

        try:
            to_kill = int(word2vec_input(self.message.content, replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send("something went wrong")
            return

        all_items = await self.get_user_docs(item_name, str(self.message.author))

        if to_kill > len(all_items) - 1:
            await self.message.channel.send("something went wrong")
        else:
            id_to_delete = all_items[to_kill]['_id']
            await self.delete_doc(item_name, id_to_delete)
            await self.message.channel.send("item {} removed!".format(to_kill))


class Obj2Dict:

    def __init__(self, obj):
        dct = {}

        master_attr = vars(Master())

        for attr, value in vars(obj).items():
            if attr in master_attr:
                if attr == 'message':
                    dct.update({'username': str(value.author),
                                'channel id': int(value.channel.id),
                                'message': str(value.content),
                                'created at': str(value.created_at)})
                else:
                    pass
            else:
                if attr == 'name':
                    dct.update({'name': value.lower()})
                else:
                    dct.update({attr: value})

        dct.update({'text': str(obj)})

        self.dct = dct

    async def make_document(self, db):
        collection_name = self.dct['name']
        collection = db[collection_name]
        return await collection.insert_one(self.dct)
