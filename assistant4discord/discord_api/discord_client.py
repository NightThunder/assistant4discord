import discord
import logging
from assistant4discord.data.logger import setup_logger
from assistant4discord.assistant.messenger import Messenger
from assistant4discord.assistant.mongodb_reinitialize import Reinitializer
import motor.motor_asyncio


logging.basicConfig(level=logging.INFO)


class MyClient(discord.Client):
    def __init__(self, reinitializer=None, messenger=None, log_chat=False, chat_logger=None, *args, **kwargs):
        """
        Parameters
        ----------
        reinitializer: obj
            Loads commands from mongodb.
        messenger: obj
            Imports commands when initialized. Used for message -> command mapping.
        log_chat: bool, optional
            Logs all chat that bot can see when True.
        chat_logger: func
            Logging function. Provided in data/logger.py .

        References
        ----------
        https://discordpy.readthedocs.io/en/latest/api.html#client
        https://discordpy.readthedocs.io/en/latest/api.html#event-reference
        https://discordpy.readthedocs.io/en/latest/api.html#message
        https://discordpy.readthedocs.io/en/latest/api.html#dmchannel
        """
        super().__init__(*args, **kwargs)
        self.log_chat = log_chat
        self.reinitializer = reinitializer
        self.messenger = messenger
        self.chat_logger = chat_logger

    async def on_ready(self):
        """ Reinitializes commands from mongodb. Initializes commands with initialize method. Displays bot name and id on login."""

        await self.reinitializer.reinitialize()

        initialized = self.messenger.initializer()

        for command in initialized:
            await command.initialize()

        print("Logged in as: {}, {}".format(self.user.name, self.user.id))

    async def on_message(self, message):
        """
            If message is private then @ call is not required. This means that every message is read and processed. If
            no matching command is found do nothing.
            @<bot name> is required if message from server. If no matching command is found send error.

            Note
            ----
            Uses message_to_command function from messenger.py to get a command. If function return not None call
            doit on command which runs the command.
        """
        if self.log_chat:
            self.chat_logger.info(
                "channel: {}, author full name: {}, author name: {}, content: {}".format(
                    message.channel,
                    message.author,
                    message.author.name,
                    message.content,
                )
            )

        if message.author == self.user:
            return

        if message.content.startswith("<@{}>".format(self.user.id)):
            message.content = message.content[22:]
            messenger = self.messenger.message_to_command(message)

            if messenger:
                await messenger.doit()
            else:
                await message.channel.send("Error: not implemented")

        elif isinstance(message.channel, discord.DMChannel):
            messenger = self.messenger.message_to_command(message)

            if messenger:
                await messenger.doit()
            else:
                # do nothing if command not detected
                pass

        else:
            # is not private message and does not start with @assistant
            pass


def run(method, discord_token, mongodb_token, log_chat, model_name=None):

    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_token)
    db = mongodb_client["assistant4discord"]

    client = MyClient()

    if log_chat:
        client.log_chat = log_chat
        client.chat_logger = setup_logger(log_name="chat.log")

    client.messenger = Messenger(method=method, db=db, client=client, model_name=model_name)
    client.reinitializer = Reinitializer(db=db, client=client, messenger=client.messenger)
    client.run(discord_token)
