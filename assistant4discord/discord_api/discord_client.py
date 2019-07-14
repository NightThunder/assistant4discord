import discord
import logging
from assistant4discord.data.logger import setup_logger
from assistant4discord.assistant.messenger import Messenger


logging.basicConfig(level=logging.INFO)


class MyClient(discord.Client):

    def __init__(self, messenger=None, log_chat=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_chat = log_chat
        self.messenger = messenger
        self.log_chat = log_chat
        self.chat_logger = None

    async def on_ready(self):
        print('Logged in as: {}, {}'.format(self.user.name, self.user.id))

    async def on_message(self, message):
        if self.log_chat:
            self.chat_logger.info('channel: {}, author full name: {}, author name: {}, content: {}'
                                  .format(message.channel, message.author, message.author.name, message.content))

        if message.author == self.user:
            return

        if message.content.startswith('<@{}>'.format(self.user.id)):
            message.content = message.content[22:]
            messenger = self.messenger.message_to_command(message)

            if messenger:
                await messenger.doit()
            else:
                await message.channel.send('Error: not implemented')


def run(method, model_name, my_token, log_chat):

    client = MyClient()

    if log_chat:
        client.log_chat = log_chat
        client.chat_logger = setup_logger(log_name='chat.log')

    client.messenger = Messenger(method=method, client=client, model_name=model_name)
    client.run(my_token)
