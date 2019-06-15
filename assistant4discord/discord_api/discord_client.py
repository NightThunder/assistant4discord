import discord
import logging
from assistant4discord.data.logger import setup_logger
from assistant4discord.assistant.messenger import Messenger


logging.basicConfig(level=logging.INFO)
chat_logger = setup_logger(log_name='chat.log')


class MyClient(discord.Client):

    def __init__(self, messenger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messenger = messenger

    async def on_ready(self):
        print('Logged in as: {}, {}'.format(self.user.name, self.user.id))

    async def on_message(self, message):
        chat_logger.info('channel: {}, author full name: {}, author name: {}, content: {}'
                         .format(message.channel, message.author, message.author.name, message.content))

        if message.author == self.user:
            return

        if message.content.startswith('<@{}>'.format(self.user.id)):
            M = self.messenger.message_to_command(message)
            if M:
                await M.doit()
            else:
                await message.channel.send('Error: not implemented')


def run(model_name, my_token):
    client = MyClient()
    client.messenger = Messenger(client=client, model_name=model_name)
    client.run(my_token)
