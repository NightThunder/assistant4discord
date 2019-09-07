from importlib import import_module
import time
import os
import inspect
from pathlib import Path
from assistant4discord.assistant.commands.helpers.mongodb_adder import AddItem


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
    def __init__(self, db, client, messenger):
        self.db = db
        self.client = client
        self.messenger = messenger

    async def get_all_docs(self, collection_name):
        """ Get all documents of a collection.

        Returns
        -------
        All documents in a collection as a list of dicts.

        """
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def load_from_db(self, obj):
        """ Makes command object from database.

        Parameters
        ----------
        obj: obj
            Command object (not yet initialized).

        Note
        ----
        Also adds _id to object. Saved channel is used mainly for timed functions (TimeIt).

        A field required in every MongoDB document. The _id field must have a unique value. You can think of the _id
        field as the document’s primary key. If you create a new document without an _id field, MongoDB automatically
        creates the field and assigns a unique BSON ObjectId.

        Returns
        -------
        None if [] in mongodb.
        Initialized object that was created from mongodb JSON with __dict__ .

        """
        command_doc = await self.get_all_docs(obj().name)

        # loop over ALL commands of ALL users in a collection of name obj().name
        for command in command_doc:
            re_obj = obj()
            re_obj.__dict__.update(command)
            re_obj.client = self.client

            if re_obj.name == "time_it":
                re_obj.commands = self.messenger.commands
                re_obj.sim = self.messenger.sim

            await self.timer_check(re_obj, command)
            await self.add_item(re_obj)

    @staticmethod
    async def timer_check(re_obj, command):
        """ Corrections for asyncio.sleep().

        Note
        ----
        Only updates local object with time_to_message.

        """
        try:
            created_on = command["created_on"]
            time_to_message = command["time_to_message"]

            new_time_to_message = time_to_message - (time.time() - created_on)
            re_obj.time_to_message = new_time_to_message

        except (KeyError, TypeError):
            return

    async def add_item(self, re_obj):
        """ Adds initialized object (command) to event loop."""

        ext = AddItem()
        ext.client = self.client
        ext.db = self.db
        await ext.AddItem_doit(re_obj)

    @staticmethod
    def get_helpers():
        """ Adds all helper class names to a list.

        Helper objects can be inherited in extensions. Importing inherited objects results in an error.

        """
        helpers = []

        dir_path = str(Path(__file__).parents[1]) + "/assistant/commands/helpers"
        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith(".py") and "__init__" not in file:

                module_name = "assistant4discord.assistant.commands.helpers.{}".format(file[:-3])

                module = import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and str(obj.__module__).count(".") == 4:
                        if name not in helpers:
                            helpers.append(name)

        return helpers

    async def reinitialize(self):
        """ Creates (reinitializes) commands from extension classes using mongodb."""

        helpers = self.get_helpers()

        dir_path = str(Path(__file__).parents[1]) + "/assistant/commands/extensions"
        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith(".py") and "__init__" not in file:

                module_name = "assistant4discord.assistant.commands.extensions.{}".format(file[:-3])

                module = import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and str(obj.__module__).count(".") == 4:
                        if name not in helpers:
                            await self.load_from_db(obj)
