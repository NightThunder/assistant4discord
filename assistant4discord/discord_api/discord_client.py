import discord
import asyncio
import logging
from assistant4discord.assistant.commander import *


logging.basicConfig(level=logging.INFO)


class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged in as: {}, {}'.format(self.user.name, self.user.id))

    async def on_message(self, message):
        chat_logger.info('channel: {}, author full name: {}, author name: {}, content: {}'.format(message.channel, message.author, message.author.name, message.content))

        if message.author == self.user:
            return

        if message.content.startswith('<@{}>'.format(self.user.id)):
            await message.channel.send('You have summoned me!')

        if message.content.startswith('ping'):
            await ping(message)

        if message.content.startswith('sleep'):
            await sleeper(message)


async def ping(message):
    await message.channel.send('{} ms'.format(round(client.latency * 1000)))


async def sleeper(message):
    await message.channel.send('going to sleep')
    await asyncio.sleep(10)
    await message.channel.send('slept for 10 s')


def setup_chat_logger(name=__name__, log_name='new.log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s'):
    from pathlib import Path

    log_file = str(Path(__file__).parents[2]) + '/data/' + log_name

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(format)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


chat_logger = setup_chat_logger(log_name='chat.log')

my_token = open('../token.txt', 'r').read()
client = MyClient()
client.run(my_token)
