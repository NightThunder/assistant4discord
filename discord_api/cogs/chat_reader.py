from discord.ext import commands
import logging


class ChatReader(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        chat_logger.info('channel: {}, author full name: {}, author name: {}, content: {}'
                         .format(message.channel, message.author, message.author.name, message.content))

        if message.author == self.bot.user:
            return

        if 'hi there' in message.content:
            await message.channel.send('hello')


def setup_chat_logger(name=__name__, log_name='new_log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s'):
    from pathlib import Path

    log_file = str(Path(__file__).parents[2]) + '/data/' + log_name

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(format)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def setup(bot):
    bot.add_cog(ChatReader(bot))


chat_logger = setup_chat_logger(log_name='chat_log')
