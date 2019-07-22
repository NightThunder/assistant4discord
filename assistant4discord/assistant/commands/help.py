from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master


class Help(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'help'

    async def doit(self):

        message = self.message.content

        if len(word2vec_input(message)) > 1:
            for i, (command_str, command) in enumerate(self.commands.items()):
                if command_str.lower() in message.lower() and command_str != 'Help':
                    await self.message.channel.send(command.help)
                    break

                if i == len(self.commands) - 1:
                    await self.message.channel.send('Command not found!')

        else:
            command_str = '```My commands: '
            for i, (command_str_, command) in enumerate(self.commands.items()):
                if command.special:
                    if command.special.get('hidden'):
                        continue

                command_str += command_str_ + ', '

            command_str = command_str[:-2]
            command_str += '\nType help <command> for more info!```'

            await self.message.channel.send(command_str)
