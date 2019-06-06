from discord.ext import commands


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def ping(self, ctx):
        await ctx.send('{} ms'.format(round(self.bot.latency * 1000)))
