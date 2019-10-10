import asyncio
import inspect
import discord
import time
from a4d.assistant.commands.helpers.master import Master
from .extend import ExtError


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
        await self.db[self.name].delete_one({"_id": _id})

    async def find_doc(self, _id):
        found = await self.db[self.name].find_one({"_id": _id})

        if found:
            return found
        else:
            return None

    async def set_return_channel(self, item_obj):
        """ Set channel_type and response_channel.

        If special has dm response change response_channel to dm. Else keep channel from where message was sent.

        Parameters
        ----------
        item_obj: obj
            Command object.

        Returns
        -------
        Updated command object

        """
        if isinstance(self.message.channel, discord.DMChannel):
            channel_type = "DMChannel"
            response_channel = self.message.channel.id
        elif self.special.get("response", None) == "dm":
            channel_type = "DMChannel"
            dm = await self.message.author.create_dm()
            response_channel = dm.id
        else:
            channel_type = "GroupChannel"
            response_channel = self.message.channel.id

        item_obj.channel_type = channel_type
        item_obj.response_channel = response_channel

        return item_obj

    @staticmethod
    def correct_times(item_obj, t_run):
        """ Correction for 'at' keyword in message, correction for server downtime.

        Parameters
        ----------
        item_obj: obj
            Command object.
        t_run: float
            Needed time for coro_doit() functions. Run time + asyncio sleep time.
            Used for time adjustment, item_obj.send (~0.2 sec) and item_obj.doit (~0.3 sec for timer).

        Used for updating time_to_message attribute in item_obj.

        Content that couldn't be sent when it was supposed to (due to shutdown) is sent on next bot start. When it's
        possible send one event immediately and adjust next one accordingly so it lines up with what was supposed to happen.

        Returns
        -------
        New time to message.

        """
        t_now = time.time()
        t_fix = t_now - t_run - item_obj.time_to_message

        x = t_now - item_obj.created_on

        if item_obj.time_to_message >= 0:
            t = item_obj.every - t_fix
        else:
            k = x // item_obj.every
            t = x - k * item_obj.every - t_fix

        return t

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

        t2 = 0       # time correction for Obj2dict

        while True:

            if make_db_entry:
                res = await Obj2Dict(item_obj).make_doc(self.db)
                doc_id = res.inserted_id
                make_db_entry = False

            else:
                t1 = time.time()    # measures how long coro_doit() takes to complete

                item_obj.time_to_message = item_obj.time_to_message - t2
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
                    await item_obj.send("{}".format(e))
                    return

                # check if something in message if len > 2000 split message
                # None if doit() doesn't return anything (timer_class)
                if discord_send is None or len(discord_send) == 0:
                    pass
                else:
                    for i in range(int(len(discord_send) / 2000) + 1):
                        await item_obj.send(discord_send[i * 2000: (i + 1) * 2000])

                # if every is false we are done else we update doc and loop
                if item_obj.every is False:
                    await self.delete_doc(doc_id)
                    return
                else:
                    item_obj.time_to_message = self.correct_times(item_obj, t1)
                    t2_ = time.time()
                    item_obj.created_on = t2_      # updates object's time
                    await Obj2Dict(item_obj).update_doc(self.db, doc_id)
                    t2 = time.time() - t2_

    async def AddItem_doit(self, item):
        """ Core method.

        Parameters
        ----------
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
        ExtError if something wrong in extension.

        """
        if "__module__" in item.__dict__:
            item_obj = item(client=self.client, message=self.message)
        else:
            item_obj = item

        self.is_re_obj = getattr(item_obj, "_id", False)
        self.name = item_obj.name
        self.is_todo_async = inspect.iscoroutinefunction(item.doit)

        # if command has initialize==True, don't send anything
        initialize = getattr(item_obj, "initialize", False)

        # check if called from mongodb_reinitialize
        if self.is_re_obj:
            if getattr(item_obj, "use_asyncio", False):
                task = self.client.loop.create_task(self.coro_doit(item_obj))
                if not task:
                    return
            else:
                pass
        else:
            # set channel_type and response_channel also update special in item_obj
            if not initialize:
                item_obj = await self.set_return_channel(item_obj)
                item_obj.special = self.special

            # run on initialization if True
            if getattr(item_obj, "run_on_init", False):
                try:
                    if self.is_todo_async:
                        await item_obj.doit()
                    else:
                        item_obj.doit()

                except ExtError as e:
                    if not initialize:
                        await item_obj.send("{}".format(e))
                        return None
                    else:
                        return None
            else:
                pass

            # check if extension uses asyncio
            if getattr(item_obj, "use_asyncio", False):
                if not initialize:
                    await item_obj.send(str(item_obj))

                # add coro_doit to event loop
                task = self.client.loop.create_task(self.coro_doit(item_obj))
                if not task:
                    return
            else:
                await Obj2Dict(item_obj).make_doc(self.db)
                if not initialize:
                    await item_obj.send(str(item_obj))


class Obj2Dict:
    """ Transform command object __dict__ to mongodb readable dict."""

    def __init__(self, obj):
        dct = {}

        master_attr = Master().__dict__

        for attr, value in obj.__dict__.items():
            if attr in master_attr:
                if obj.message is not None:
                    if attr == "message":
                        dct.update(
                            {
                                "username": str(value.author),
                                "author_id": value.author.id,
                                "channel_id": value.channel.id,
                                "original_message": value.content,
                                "message_received_on": value.created_at,
                            }
                        )
                    else:
                        pass

                if attr == "channel_type":
                    dct.update({"channel_type": value})
                elif attr == "response_channel":
                    dct.update({"response_channel": value})
                else:
                    pass

            else:
                if attr == "name":
                    dct.update({"name": value})
                else:
                    if value is not None:
                        dct.update({attr: value})
                    else:
                        pass

        dct.update({"text": str(obj)})

        self.dct = dct

    async def make_doc(self, db):
        collection_name = self.dct["name"]
        return await db[collection_name].insert_one(self.dct)

    async def update_doc(self, db, _id):
        collection_name = self.dct["name"]
        return await db[collection_name].replace_one({"_id": _id}, self.dct)
