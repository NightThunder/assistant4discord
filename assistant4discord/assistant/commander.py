from discord.ext import commands


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('{} ms'.format(round(self.bot.latency * 1000)))


# TODO fix this
# probably with MyClient: https://github.com/Rapptz/discord.py/blob/master/examples/background_task.py
