from a4d.assistant.commands.helpers.master import Master


class Ping(Master):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***Ping help***\n"
            "Ping discord server and return response time in ms.\n"
            "Call: ping```"
        )
        self.call = "ping"

    async def doit(self):
        await self.send("{} ms".format(round(self.client.latency * 1000)))
