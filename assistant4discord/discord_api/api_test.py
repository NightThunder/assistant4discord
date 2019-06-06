# https://discordpy.readthedocs.io/en/latest/index.html
# https://www.youtube.com/watch?v=xdg39s4HSJQ&list=PLzMcBGfZo4-kdivglL5Dt-gY7bmdNQUJu&index=1
# https://www.youtube.com/watch?v=ELUxJsQK290&list=PLQVvvaa0QuDf5LApiJp_I5lmJ0zNT6Po4&index=1
# https://pythonprogramming.net/discordpy-basic-bot-tutorial-introduction/
# https://www.youtube.com/watch?v=nW8c7vT6Hl4&list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ&index=1

from discord.ext import commands
import os
import logging


logging.basicConfig(level=logging.INFO)

# bot = commands.Bot(command_prefix=commands.when_mentioned_or())
bot = commands.Bot(command_prefix='.')


# @bot.command()
# async def load(ctx, extension):
#     bot.load_extension('cogs.{}'.format(extension))
#
#
# @bot.command()
# async def unload(ctx, extension):
#     bot.unload_extension('cogs.{}'.format(extension))


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension('cogs.{}'.format(filename[:-3]))
        print('loaded: {}'.format(filename))


my_token = open('../token.txt', 'r').read()
bot.run(my_token)
