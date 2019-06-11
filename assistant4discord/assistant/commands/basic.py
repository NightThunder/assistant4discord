import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input


class Master:

    def __init__(self, client=None, message=None, similarity=None):
        """ Base class for commands.

        Args:
            client: discord client object
            message: discord message object
            similarity: Similarity object from assistant4discord.nlp_tasks.similarity
        """
        self.client = client
        self.message = message
        self.sim = similarity


class Ping(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.call = 'ping'

    async def doit(self):
        await self.message.channel.send('{} ms'.format(round(self.client.latency * 1000)))


class After10(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'sleep'

    async def doit(self):
        await self.message.channel.send('sleeping for 10')
        await asyncio.sleep(10)
        await self.message.channel.send('woken up after 10')


class WordSim(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'similarity'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        similarity = self.sim.model.similarity(sent[-1], sent[-2])

        await self.message.channel.send(str(similarity))
