import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input


class Ping:

    def __init__(self, **kwargs):
        if kwargs:
            self.client = kwargs['client']
            self.message = kwargs['message']

        self.call = 'ping'

    async def doit(self):
        await self.message.channel.send('{} ms'.format(round(self.client.latency * 1000)))


class After10:

    def __init__(self, **kwargs):
        if kwargs:
            self.message = kwargs['message']

        self.call = 'sleep'

    async def doit(self):
        await self.message.channel.send('sleeping for 10')
        await asyncio.sleep(10)
        await self.message.channel.send('woken up after 10')


class WordSim:

    def __init__(self, **kwargs):
        if kwargs:
            self.message = kwargs['message']
            self.sim = kwargs['similarity']

        self.call = 'word similarity'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        print(sent)
        similarity = self.sim.model.similarity(sent[-1], sent[-2])

        await self.message.channel.send(str(similarity))


# TODO fix similarities questions that have same input as command call (input: word similarity ping, latency)
