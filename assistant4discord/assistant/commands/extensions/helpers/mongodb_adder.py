import asyncio
import inspect
from assistant4discord.assistant.commands.master.master_class import Master


class AddItem(Master):
    """ Persistent storage.

    Inherit this class in your command if you need to save an object that represents a command to a database.

    Types of commands:
        (i) normal command (static)
            Doesn't use any asyncio. AddItem saves it to mongodb. Remains in database until owner removes it.
        (ii) async command
            use_asyncio = True
            Uses asyncio, aiohttp, ...
            AddItem saves it to mongodb and initializes a timer. Removed when timer is up. Can also be removed by user.
    """

    def __init__(self):
        """
        Other Parameters
        ----------------
        name: str
            Name of command object.
        is_todo_async: bool or None
            True if method async.
        is_re_obj: bool or None
            True if object initialized form database.
        """
        super().__init__()
        self.name = None
        self.is_todo_async = None
        self.is_re_obj = None

    @staticmethod
    def obj_error_check(item_obj):
        """ Check if any attribute None.

        Parameters
        ----------
        item_obj: obj
            Command object.

        Returns
        -------
        bool
            True if found None in object attributes else False.
        """
        master_attr = Master().__dict__

        for attr, value in item_obj.__dict__.items():
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
            Command object.
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
                # looks in database for a specific document
                found = await self.find_doc(doc_id)

                if found:
                    channel = self.client.get_channel(found['channel id'])
                else:
                    return

                # works with reinitializer (dynamic time change) object has static time_to_message
                await asyncio.sleep(found['time_to_message'])

                # if not found it was deleted by user
                if not await self.find_doc(doc_id):
                    return

                # check if to_do is async def
                if self.is_todo_async:
                    discord_send = await item_obj.todo()
                else:
                    discord_send = item_obj.todo()

                # check if something in message if len > 2000 split message
                if len(discord_send) == 0:
                    pass
                else:
                    for i in range(int(len(discord_send) / 2000) + 1):
                        await channel.send(discord_send[i * 2000: (i + 1) * 2000])

                # if every is false we are done else we update doc and loop
                if item_obj.every is False:
                    await self.delete_doc(doc_id)
                    return
                else:
                    await Obj2Dict(item_obj).update_doc(self.db, doc_id)

    async def AddItem_doit(self, item_obj):
        """ Core method.

        Parameters
        item_obj: obj
            Command object passed from commands directory.

        If __module__ in dict of item_obj that means that no Master attributes were given in that case assume only client
        and message are needed.
        Set self.is_re_obj if _id in attributes (only if called from mongodb_reinitialize). Set self.name. Set self.is_todo_async
        if item_obj has async def todo().
        If is_re_obj skip all initialization steps.
        Initialization is done for 2 cases. If async add it to event loop else write it to mongodb.

        Note
        ----
        AttributeErrors are for when self.message == None. Happens if command has initialize method.
        """

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
    """ Transform command object __dict__ to mongodb readable dict."""

    def __init__(self, obj):
        dct = {}

        master_attr = Master().__dict__

        for attr, value in obj.__dict__.items():
            if attr in master_attr:
                if obj.message:
                    if attr == 'message':
                        dct.update({'username': str(value.author),
                                    'channel id': int(value.channel.id),
                                    'message': str(value.content),
                                    'message created at': str(value.created_at)})
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
