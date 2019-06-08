from assistant4discord.nlp_tasks.similarity import Similarity
from importlib import import_module
import os
import inspect


class Commander:

    def __init__(self, dir_path=None):
        self.commands = self.get_commands(dir_path)
        self.calls = self.get_command_calls()

    @staticmethod
    def get_commands(dir_path):
        """Get all commands from directory.

        Args:
            dir_path: directory path

        Returns: list of command objects
        """
        command_dct = {}

        if not dir_path:
            dir_path = os.path.dirname(os.path.realpath(__file__)) + '/commands'

        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith('.py') and '__init__' not in file:
                module = import_module('.{}'.format(file[:-3]), package='commands')
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        command_dct['{}'.format(name)] = obj

        return command_dct

    def get_command_calls(self):
        command_calls = []

        for command_str, command in self.commands.items():
            if command_str != 'Basic':
                command_calls.append(command().call)

        return command_calls

    def message_to_command(self, message: str, client: object):
        self.commands['Basic'](message, client)

        sim = Similarity('5days_askreddit_model.kv').message_x_command_sim(message, self.calls)
        return sim


C = Commander()
print(C.message_to_command('whats my ping', 'client'))
