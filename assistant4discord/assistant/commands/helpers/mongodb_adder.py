import asyncio
import inspect
import discord
from assistant4discord.assistant.commands.helpers.master import Master
from.extend import ExtError


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
                await asyncio.sleep(item_obj.time_to_message)

                # if not found it was deleted by user
                if not await self.find_doc(doc_id):
                    return

                # check if to_do is async def
                try:
                    if self.is_todo_async:
                        discord_send = await item_obj.doit()
                    else:
                        discord_send = item_obj.doit()

                except ExtError as e:
                    await self.message.channel.send("{}".format(e))
                    return
                    
                # check if something in message if len > 2000 split message
                # if TypeError this is timer with function and not string
                try:
                    if len(discord_send) == 0:
                        pass
                    else:
                        for i in range(int(len(discord_send) / 2000) + 1):
                            await item_obj.send(discord_send[i * 2000: (i + 1) * 2000])
                except TypeError:
                    pass

                # if every is false we are done else we update doc and loop
                if item_obj.every is False:
                    await self.delete_doc(doc_id)
                    return
                else:
                    # correction if 'at' keyword in message
                    item_obj.time_to_message = item_obj.every
                    await Obj2Dict(item_obj).update_doc(self.db, doc_id)

    async def AddItem_doit(self, item):
        """ Core method.

        Parameters
        item: obj
            Command object passed from commands directory.

        If __module__ in dict of item that means that no Master attributes were given in that case assume only client
        and message are needed.
        Set self.is_re_obj if _id in attributes (only if called from mongodb_reinitialize). Set self.name. Set self.is_todo_async
        if item_obj has async def doit().
        If is_re_obj skip all initialization steps.
        Run doit() once if run_on_init.
        Initialization is done for 2 cases. If async add it to event loop else write it to mongodb.

        Raises
        ------
        AttributeError when self.message == None. Happens if command has initialize method.
        ExtError if something wrong in extension.

        """
        if '__module__' in item.__dict__:
            item_obj = item(client=self.client, message=self.message)
        else:
            item_obj = item

        self.is_re_obj = getattr(item_obj, '_id', False)
        self.name = item_obj.name
        self.is_todo_async = inspect.iscoroutinefunction(item.doit)

        if self.is_re_obj:
            if getattr(item_obj, 'use_asyncio', False):
                task = self.client.loop.create_task(self.coro_doit(item_obj))
                if not task:
                    return
            else:
                pass
        else:
            # run on initialization if True
            if getattr(item_obj, 'run_on_init', False):
                try:
                    if self.is_todo_async:
                        await item_obj.doit()
                    else:
                        item_obj.doit()

                except ExtError as e:
                    try:
                        await self.message.channel.send("{}".format(e))
                        return

                    except AttributeError:
                        raise ExtError
            else:
                pass

            if getattr(item_obj, 'use_asyncio', False):                          # check if helper uses asyncio
                await self.message.channel.send(str(item_obj))
                task = self.client.loop.create_task(self.coro_doit(item_obj))    # add coro_doit to event loop

                if not task:
                    return
            else:
                await Obj2Dict(item_obj).make_doc(self.db)
                try:
                    await self.message.channel.send(str(item_obj))
                except AttributeError:
                    pass


class Obj2Dict:
    """ Transform command object __dict__ to mongodb readable dict."""

    def __init__(self, obj):
        dct = {}

        master_attr = Master().__dict__

        for attr, value in obj.__dict__.items():
            if attr in master_attr:
                if obj.message is not None:
                    if attr == 'message':
                        dct.update({'username': str(value.author),
                                    'author_id': int(value.author.id),
                                    'channel_id': int(value.channel.id),
                                    'original_message': str(value.content),
                                    'message_received_on': str(value.created_at)})

                        if isinstance(value.channel, discord.DMChannel):
                            dct.update({'channel_type': 'DMChannel'})
                        else:
                            dct.update({'channel_type': 'GroupChannel'})

                    else:
                        pass
                else:
                    pass
            else:
                if attr == 'name':
                    dct.update({'name': value})
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
