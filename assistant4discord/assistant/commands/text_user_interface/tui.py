import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master


class AddItem(Master):
    """
        self.all_items: list of all items (self.item objects)
        self.time_coro: if self.item uses asyncio.sleep()
        self.send_str: send this to discord
        self.item: helper object

        item helper (obj): must have __str__ if time_coro must have __str__, self.time_to_message, self.to_do, self.every
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_items = []
        self.time_coro = False

    def remove_dead_items(self):

        all_active_items = []

        for item in self.all_items:
            if not item.task.done():
                all_active_items.append(item)

        self.all_items = all_active_items

    async def coro_doit(self, item_obj):

        while True:
            await asyncio.sleep(item_obj.time_to_message)
            await self.message.channel.send(item_obj.to_do)

            if item_obj.every is False:
                return

    async def AddItem_doit(self, item_obj):
        Item = item_obj(client=self.client, message=self.message)

        send_str = str(Item)

        if self.time_coro:

            if Item.time_to_message and Item.to_do:
                await self.message.channel.send(send_str)

                task = self.client.loop.create_task(self.coro_doit(Item))
                setattr(Item, 'task', task)
                self.all_items.append(Item)
            else:
                await self.message.channel.send('something went wrong')

        else:
            if Item:
                self.all_items.append(Item)
                await self.message.channel.send(send_str)
            else:
                await self.message.channel.send('something went wrong')


class ShowItems(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def ShowItems_doit(self, item_obj_str):

        add_items_obj = self.commands[item_obj_str]
        add_items_obj.remove_dead_items()
        all_items = add_items_obj.all_items

        item_str = ''
        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author and not item.task.done():
                item_str += '**{}:** {}\n'.format(i, str(item))

                if i != len(all_items) - 1:
                    item_str += '--------------------\n'

                n_items += 1

        if n_items != 0:
            await self.message.channel.send(item_str)
        else:
            await self.message.channel.send('something went wrong')


class RemoveItem(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def RemoveItem_doit(self, item_obj_str):

        add_items_obj = self.commands[item_obj_str]
        add_items_obj.remove_dead_items()
        all_items = add_items_obj.all_items

        try:
            to_kill = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong')
            return

        n_items = 0
        for i, item in enumerate(all_items):
            if item.message.author == self.message.author and not item.task.done() and i == to_kill:
                item.task.cancel()
                break
            else:
                n_items += 1

        if to_kill > n_items:
            await self.message.channel.send('something went wrong')
        else:
            await self.message.channel.send('item {} removed!'.format(to_kill))
