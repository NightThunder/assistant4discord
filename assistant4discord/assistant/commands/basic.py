import asyncio


class Basic:

    def __init__(self, message=None, client=None):
        self.message = message
        self.client = client


class Ping(Basic):

    def __init__(self, *args):
        super().__init__(*args)
        self.call = 'ping'

    async def doit(self):
        await self.message.channel.send('{} ms'.format(round(self.client.latency * 1000)))


class After10(Basic):

    def __init__(self, *args):
        super().__init__(*args)
        self.call = 'sleep'

    async def doit(self):
        await self.message.channel.send('sleeping for 10')
        await asyncio.sleep(10)
        await self.message.channel.send('woken up after 10')

