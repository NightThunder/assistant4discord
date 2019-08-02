from importlib import import_module
import time
import os
import inspect
from pathlib import Path
from assistant4discord.assistant.commands.extensions.helpers.mongodb_adder import AddItem


class Reinitializer:
    """ Load saved commands from mongodb on startup. This makes a bot persistent.

    Note
    ----
    Document (doc here) is a record in a MongoDB collection and the basic unit of data in MongoDB. Documents are analogous to
    JSON objects but exist in the database in a more type-rich format known as BSON.

    Collection (command class) is a grouping of MongoDB documents. A collection is the equivalent of an RDBMS table. A collection exists within a
    single database. Collections do not enforce a schema. Documents within a collection can have different fields.
    Typically, all documents in a collection have a similar or related purpose.

    Each command class is its own collection. Command collections hold instances of command objects as JSON (__dict__ of object).

    References
    ----------
    https://api.mongodb.com/python/current/tutorial.html
    https://docs.mongodb.com/manual/
    https://www.mongodb.com/cloud/atlas
    https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
    https://www.youtube.com/watch?v=BPvg9bndP1U
    """
    def __init__(self, db, client):
        self.db = db
        self.client = client

    async def get_all_docs(self, collection_name):
        """ Get all documents of a collection.

        Returns
        -------
        All documents in a collection as a list of dicts.
        """
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def update_doc(self, collection_name, replace_lst):
        """ Updates a document.

        Parameters
        ----------
        collection_name: str
        replace_lst: list of dicts
            [{OLD}, {'$set': {NEW}}]
        """
        await self.db[collection_name].update_one(replace_lst[0], replace_lst[1])

    async def load_from_db(self, obj):
        """ Makes command object from database.

        Parameters
        ----------
        obj: obj
            Command object (not yet initialized).

        Note
        ----
        Also adds _id to object.

        A field required in every MongoDB document. The _id field must have a unique value. You can think of the _id
        field as the document’s primary key. If you create a new document without an _id field, MongoDB automatically
        creates the field and assigns a unique BSON ObjectId.

        Returns
        -------
        None if [] in mongodb.
        Initialized object that was created from mongodb JSON with __dict__ .
        """
        command_doc = await self.get_all_docs(obj().name)
        re_obj = None

        for command in command_doc:
            re_obj = obj()
            re_obj.__dict__.update(command)
            re_obj.client = self.client

        return re_obj

    async def timer_check(self, re_obj):
        """ Corrections for asyncio.sleep()."""

        created_on = getattr(re_obj, 'created_on', False)
        time_to_message = getattr(re_obj, 'time_to_message', False)

        if created_on and time_to_message:
            new_time_to_message = time_to_message - (int(time.time()) - created_on)
            replace_lst = [{'time_to_message': time_to_message}, {'$set': {'time_to_message': new_time_to_message}}]

            if new_time_to_message < 0:
                await self.update_doc(re_obj.name, replace_lst)
            else:
                await self.update_doc(re_obj.name, replace_lst)
        else:
            return None

    async def add_item(self, re_obj):
        """ Adds initialized object (command) to event loop."""

        ext = AddItem()
        ext.client = self.client
        ext.db = self.db
        await ext.AddItem_doit(re_obj)

    async def reinitialize(self):
        """ Creates (reinitializes) commands from extension classes using mongodb."""

        dir_path = str(Path(__file__).parents[1]) + "/assistant/commands/extensions"
        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith(".py") and "__init__" not in file:

                module_name = "assistant4discord.assistant.commands.extensions.{}".format(file[:-3])

                module = import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and str(obj.__module__).count(".") == 4:
                        if name != 'Master':
                            re_obj = await self.load_from_db(obj)
                            if re_obj:
                                await self.timer_check(re_obj)
                                await self.add_item(re_obj)


# TODO: fix timer so it works with this
