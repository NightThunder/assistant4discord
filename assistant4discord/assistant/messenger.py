from assistant4discord.nlp_tasks.w2v import w2vSimilarity
from assistant4discord.nlp_tasks.tf import tfSimilarity
from importlib import import_module
import os
import inspect
import numpy as np


class Commander:

    def __init__(self, method, client, model_name=None):
        """Commands initializer.

        Args:
            method: w2v or tf
            client: discord client from discord.py
            model_name: w2v model

        Attributes:
            self.commands: dict of commands from commands dir, {'command': command obj, ...}
            self.calls: list of command calls from command objects, ['command call', ...]
            self.sim: model
        """
        self.method = method
        self.client = client
        self.commands = self.get_commands()
        self.calls = self.get_command_calls()

        # command recognition method initialization
        if self.method == 'w2v':
            self.sim = w2vSimilarity(model_name, self.calls)
        elif self.method == 'tf':
            self.sim = tfSimilarity(self.calls)
        else:
            raise ValueError

        self.set_master_attributes()

    def get_commands(self) -> dict:
        """ Load commands from assistant4discord.assistant.commands. Ignore directories inside .commands.

            Notes: each command is a class that inherits from Master and has help and call attributes. There should only
                  be commands (described above) in this directory. If a command needs more then one class make a helper
                  package inside .commands and import from there.

        Returns: {'command': command obj, ...}
        """
        command_dct = {}

        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/commands'
        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith('.py') and '__init__' not in file:

                module_name = 'assistant4discord.assistant.commands.{}'.format(file[:-3])
                module = import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and str(obj.__module__).count('.') == 3:

                        obj = obj()                                         # initialize command

                        if getattr(obj, 'special', False):                             # check if command uses method
                            if obj.special.get('method'):
                                if self.method == obj.special.get('method'):
                                    command_dct[name] = obj
                                    print('imported command: {}'.format(name))
                                else:
                                    print('NOT imported command: {}'.format(name))
                            else:
                                command_dct[name] = obj
                                print('imported command: {}'.format(name))
                        else:
                            command_dct[name] = obj
                            print('imported command: {}'.format(name))

        print('-------------------------------\nimported {} commands\n'.format(len(command_dct)))
        return command_dct

    def get_command_calls(self):
        command_calls = []

        for command_str, command in self.commands.items():
            command_calls.append(command.call)

        return command_calls

    def set_master_attributes(self):
        """ Set Master class with basic attributes.

            Notes: TimeIt is a special command that is a copy of Messenger and needs all Commander attributes. Word2vec
                   commands take Similarity class as another attribute (is not needed elsewhere). If you need Similarity
                   class in your command you can set it from here.
        """
        for command_str, command in self.commands.items():

            if command_str == 'TimeIt':
                command.sim = self.sim
                command.calls = self.calls

            elif getattr(command, 'special', False):
                if 'w2v' == command.special.get('method'):
                    command.sim = self.sim

            else:
                pass

            command.commands = self.commands
            command.client = self.client


class Messenger(Commander):
    """ Class for interacting with commands.

        Returns: chosen command if cosine similarity above 0.5 else returns None
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initializer(self):
        """ Runs once on ready and initializes some commands."""
        initialized = []

        for command_str, command in self.commands.items():
            if getattr(command, 'initialize', False):
                initialized.append(command)

        return initialized

    def message_to_command(self, message: str) -> object:

        sim_arr = self.sim.message_x_command_sim(message.content)
        picked_command_str = self.calls[int(np.argmax(sim_arr))]

        print('message:', message.content)
        for i in sim_arr.argsort()[-3:][::-1]:
            print('{}: {:.3f}'.format(self.calls[i], sim_arr[i]))

        if np.max(sim_arr) < 0.5:
            return None

        for command in self.commands.values():
            if command.call == picked_command_str:
                command.message = message
                return command
