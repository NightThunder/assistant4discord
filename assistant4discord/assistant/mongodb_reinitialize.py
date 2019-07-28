from importlib import import_module
import time
import os
import inspect
from pathlib import Path
from assistant4discord.assistant.commands.extensions.helpers.mongodb_adder import AddItem


class Reinitializer:

    def __init__(self, db, client):
        self.db = db
        self.client = client

    async def get_all_docs(self, collection_name):
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def update_doc(self, collection_name, replace_lst):
        await self.db[collection_name].update_one(replace_lst[0], replace_lst[1])

    async def load_from_db(self, obj):
        command_doc = await self.get_all_docs(obj().name)
        re_obj = None

        for command in command_doc:
            re_obj = obj()
            re_obj.__dict__.update(command)         # also adds _id to object
            re_obj.client = self.client

        return re_obj

    async def timer_check(self, re_obj):
        created_on = getattr(re_obj, 'created_on', False)
        time_to_message = getattr(re_obj, 'time_to_message', False)

        if created_on and time_to_message:
            new_time_to_message = time_to_message - (int(time.time()) - created_on)
            replace_lst = [{'time_to_message': time_to_message}, {'$set': {'time_to_message': new_time_to_message}}]

            if new_time_to_message < 0:
                await self.update_doc(re_obj.name, replace_lst)
            else:
                await self.update_doc(re_obj.name, replace_lst)

    async def add_item(self, re_obj):
        ext = AddItem()
        ext.client = self.client
        ext.db = self.db
        await ext.AddItem_doit(re_obj)

    async def reinitialize(self):
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
