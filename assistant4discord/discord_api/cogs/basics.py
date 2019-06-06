from discord.ext import commands


class Basics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {}'.format(self.bot.user))

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('{} ms'.format(round(self.bot.latency * 1000)))

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Basics(bot))
