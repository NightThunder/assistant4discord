import asyncio
import inspect
from assistant4discord.assistant.commands.master.master_class import Master


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
        self.is_todo_async = None
        self.is_re_obj = None

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
        master_attr = Master().__dict__

        for attr, value in obj.__dict__.items():
            if attr not in master_attr and value is None:
                return True

        return False

    async def delete_doc(self, _id):
        await self.db[self.name].delete_one({'_id': _id})

    async def find_doc(self, _id):
        found = await self.db[self.name].find_one({'_id': _id})

        if found:
            return found
        else:
            return None

    async def coro_doit(self, item_obj):
        """ loop.create_task function.

        Parameters
        ----------
        item_obj: obj
            Command object
        self.is_todo_async: bool
            True if to_do a coroutine.
        """
        if self.is_re_obj:
            make_db_entry = False
            doc_id = item_obj._id
        else:
            make_db_entry = True

        while True:

            if make_db_entry:
                res = await Obj2Dict(item_obj).make_doc(self.db)
                doc_id = res.inserted_id
                make_db_entry = False

            else:
                # noinspection PyUnboundLocalVariable
                found = await self.find_doc(doc_id)

                if found:
                    channel = self.client.get_channel(found['channel id'])
                else:
                    return

                await asyncio.sleep(found['time_to_message'])

                # check if to_do is async def
                if self.is_todo_async:
                    discord_send = await item_obj.todo()
                else:
                    discord_send = item_obj.todo()

                # check if something in message
                # just in case len() > 2000 (max message length for discord)
                if len(discord_send) == 0:
                    pass
                else:
                    for i in range(int(len(discord_send) / 2000) + 1):
                        await channel.send(discord_send[i * 2000: (i + 1) * 2000])

                # if every is false we are done else we loop
                if item_obj.every is False:
                    await self.delete_doc(doc_id)
                    return
                else:
                    await Obj2Dict(item_obj).update_doc(self.db, doc_id)

    async def AddItem_doit(self, item_obj):
        """ Adds item to all_items. If use_asyncio create task and add it to event loop.

        Parameters
        ----------
        item_obj: obj
            Command object
        """

        # initialize helper object
        if '__module__' in item_obj.__dict__:
            Item = item_obj(client=self.client, message=self.message)
        else:
            Item = item_obj

        self.is_re_obj = getattr(Item, '_id', False)
        self.name = Item.name
        self.is_todo_async = inspect.iscoroutinefunction(item_obj.todo)

        if self.is_re_obj:
            if getattr(Item, 'use_asyncio', False):
                task = self.client.loop.create_task(self.coro_doit(Item))
                if not task:
                    return
            else:
                pass
        else:
            # run on initialization if True
            if getattr(Item, 'run_on_init', False):
                if self.is_todo_async:
                    await Item.todo()
                else:
                    Item.todo()

            # check if all helper attributes not None
            if self.obj_error_check(Item):
                try:
                    await self.message.channel.send("something went wrong")
                    return
                except AttributeError:
                    pass
            else:
                if getattr(Item, 'use_asyncio', False):                          # check if helper uses asyncio
                    await self.message.channel.send(str(Item))
                    task = self.client.loop.create_task(self.coro_doit(Item))    # add coro_doit to event loop
                    if not task:
                        await self.message.channel.send("something went wrong")
                else:
                    await Obj2Dict(Item).make_doc(self.db)
                    try:
                        await self.message.channel.send(str(Item))
                    except AttributeError:
                        pass


class Obj2Dict:

    def __init__(self, obj):
        dct = {}

        master_attr = Master().__dict__

        for attr, value in obj.__dict__.items():
            if attr in master_attr:
                # if not getattr(obj, '_id', False):
                if obj.message:
                    if attr == 'message':
                        dct.update({'username': str(value.author),
                                    'channel id': int(value.channel.id),
                                    'message': str(value.content),
                                    'created at': str(value.created_at)})
                    else:
                        pass
                else:
                    pass
            else:
                if attr == 'name':
                    dct.update({'name': value.lower()})
                else:
                    dct.update({attr: value})

        dct.update({'text': str(obj)})

        self.dct = dct

    async def make_doc(self, db):
        collection_name = self.dct['name']
        return await db[collection_name].insert_one(self.dct)

    async def update_doc(self, db, _id):
        collection_name = self.dct['name']
        return await db[collection_name].replace_one({'_id': _id}, self.dct)
