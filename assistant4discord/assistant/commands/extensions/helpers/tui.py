from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master


class ShowItems(Master):
    """ Makes a nice text menu in discord."""

    def __init__(self):
        super().__init__()

    async def get_all_docs(self, collection_name):
        cursor = self.db[collection_name].find({})
        return await cursor.to_list(length=None)

    async def get_user_docs(self, collection_name, author):
        cursor = self.db[collection_name].find({'username': author})
        return await cursor.to_list(length=None)

    async def ShowItems_doit(self, item_obj, public=False):
        """ Shows documents of a collection for a user or all if public.

        Parameters
        ----------
        item_obj: obj
            Command name which inherits from AddItem.

        public: bool
            If True show items for this command public (means that everyone can call <show command> and see a list).

        Note
        ----
        Uses self.commands to get to command object and get its all_items.
        """
        item_name = item_obj().name

        if not item_name:
            await self.message.channel.send("something went wrong 37")
            return

        item_str = ""
        n_items = 0

        if public:
            all_items = await self.get_all_docs(item_name)

            for i, item in enumerate(all_items):
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
            await self.message.channel.send("something went wrong 66")


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
        cursor = self.db[collection_name].find({'username': author})
        return await cursor.to_list(length=None)

    async def delete_doc(self, collection_name, _id):
        await self.db[collection_name].delete_one({'_id': _id})

    async def RemoveItem_doit(self, item_obj):

        item_name = item_obj().name

        if not item_name:
            await self.message.channel.send("something went wrong 93")
            return

        try:
            to_kill = int(word2vec_input(self.message.content, replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send("something went wrong 99")
            return

        all_items = await self.get_user_docs(item_name, str(self.message.author))

        if item_name == 'mods':
            to_kill -= 1

        if to_kill > len(all_items) - 1:
            await self.message.channel.send("something went wrong 108")
        else:
            id_to_delete = all_items[to_kill]['_id']
            await self.delete_doc(item_name, id_to_delete)
            await self.message.channel.send("item {} removed!".format(to_kill))
