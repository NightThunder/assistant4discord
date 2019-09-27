from a4d.nlp_tasks.message_processing import remove_punctuation
from a4d.assistant.commands.helpers.master import Master


class ShowItems(Master):
    """ Makes a nice text menu in discord."""

    def __init__(self):
        super().__init__()

    async def get_all_docs(self, collection_name):
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def get_user_docs(self, collection_name, author):
        cursor = self.db[collection_name].find({"username": author})
        return await cursor.to_list(length=None)

    async def ShowItems_doit(self, item_obj, public=False):
        """ Shows documents of a collection for a user or all if public.

        Parameters
        ----------
        item_obj: obj
            Command name which inherits from AddItem.

        public: bool
            If True show items for this command public (means that everyone can call <show command> and see a list).

        """
        item_name = item_obj().name

        if not item_name:
            raise NameError

        item_str = ""
        n_items = 0

        if public:
            all_items = await self.get_all_docs(item_name)

            for i, item in enumerate(all_items):
                item_str += "**{}** - {}".format(i, item["text"])

                item_str += "\n-----------------------------------\n"
                n_items += 1

        else:
            user_items = await self.get_user_docs(item_name, str(self.message.author))

            for i, item in enumerate(user_items):
                if str(self.message.author) == item["username"]:
                    item_str += "**{}** - {}".format(i, item["text"])
                    item_str += "\n-----------------------------------\n"
                    n_items += 1

        item_str = item_str[:-37]

        if n_items != 0:
            await self.send(item_str)
        else:
            await self.send("Could not find any items!")


class RemoveItem(Master):
    """ Removes document from database."""

    def __init__(self):
        """ Same as ShowItems.

        Note
        ----
        Doesn't have public attribute. Items can only be removed by owner.

        """
        super().__init__()

    async def get_user_docs(self, collection_name, author):
        cursor = self.db[collection_name].find({"username": author})
        return await cursor.to_list(length=None)

    async def delete_doc(self, collection_name, _id):
        await self.db[collection_name].delete_one({"_id": _id})

    async def RemoveItem_doit(self, item_obj):

        item_name = item_obj().name

        if not item_name:
            raise NameError

        msg = remove_punctuation(self.message.content)
        to_remove = [int(msg) for msg in msg.split() if msg.isdigit()]

        if len(to_remove) == 0:
            await self.send("Could not find any index!")
            return

        all_items = await self.get_user_docs(item_name, str(self.message.author))

        out_msg = 'Removed items with index'
        out_msg_ = out_msg
        err_out_msg = 'Could not remove items with index'
        err_out_msg_ = err_out_msg

        for i in to_remove:
            if i > len(all_items) - 1:
                err_out_msg += ' {},'.format(str(i))
            else:
                id_to_delete = all_items[i]["_id"]
                await self.delete_doc(item_name, id_to_delete)
                out_msg += ' {},'.format(str(i))

        if err_out_msg != err_out_msg_ and out_msg != out_msg_:
            await self.send(err_out_msg[:-1] + '\n' + out_msg[:-1])
        elif out_msg != out_msg_:
            await self.send(out_msg[:-1])
        else:
            await self.send(err_out_msg[:-1])
