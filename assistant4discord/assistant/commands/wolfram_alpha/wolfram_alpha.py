import wolframalpha
from assistant4discord.assistant.commands.basic import Master


class Wolfram(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'wolfram'
        self.help = 'Wolfram alpha query.'
        self.token = open('./token.txt', 'r').read()

    async def doit(self):
        client = wolframalpha.Client(self.token)
        res = client.query(self.message.content[28:])
        output = next(res.results).text

        await self.message.channel.send(output)
