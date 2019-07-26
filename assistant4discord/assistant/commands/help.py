from .master.master_class import Master
from assistant4discord.nlp_tasks.message_processing import word2vec_input


class Help(Master):

    def __init__(self):
        super().__init__()
        self.call = "help"

    async def doit(self):
        """
        If len(message) > 1, loop over all help attributes of all objects and send help str of the right one.
        If len(message) == 1, list all non hidden commands.

        Raises
        ------
        Command not found!
            If command of that name was noit found
        """

        message = self.message.content

        if len(word2vec_input(message)) > 1:
            for i, (command_str, command) in enumerate(self.commands.items()):
                if command_str.lower() in message.lower() and command_str != "Help":
                    await self.message.channel.send(command.help)
                    break

                if i == len(self.commands) - 1:
                    await self.message.channel.send("Command not found!")

        else:
            command_str = "```My commands: "
            for i, (command_str_, command) in enumerate(self.commands.items()):
                if command.special:
                    if command.special.get("hidden"):
                        continue

                command_str += command_str_ + ", "

            command_str = command_str[:-2]
            command_str += "\nType help <command> for more info!```"

            await self.message.channel.send(command_str)
