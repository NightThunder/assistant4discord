from assistant4discord.nlp_tasks.w2v import w2vSimilarity
from assistant4discord.nlp_tasks.tf import tfSimilarity
from importlib import import_module
import os
import inspect
import numpy as np


class Commander:
    """ Initialize message -> command method. Import commands. Set command attributes. """

    def __init__(self, method, db, client, model_name):
        """
        Parameters
        ----------
        method: str
            What method to use for message to commend conversion.
            w2v (word to vector) or tf (term frequency)
        client: obj
            Discord client.
        model_name: str, optional
            If w2v model name which is passed to gensim.

        Other Parameters
        ----------------
        commands: dict
            Dictionary of command objects. {'command str': command obj, ...}.
        calls: list of str
            List of command calls. Calls are set in command objects.
        sim: obj
            This object represents a word model. w2v or tf model.

        Raises
        ------
        ValueError
            If no or wrong method name in __main__ .
        """
        self.method = method
        self.db = db
        self.client = client
        self.commands = self.get_commands()
        self.calls = self.get_command_calls()

        if self.method == "w2v":
            self.sim = w2vSimilarity(model_name, self.calls)
        elif self.method == "tf":
            self.sim = tfSimilarity(self.calls)
        else:
            raise ValueError

        # set commands dict, client and sim
        self.set_master_attributes()

    def get_commands(self):
        """ Load commands from assistant4discord/assistant/commands/. Ignore directories inside /commands

        Note
        ----
        Each command is a class that inherits from Master and must have: help attribute, call attribute and doit method.
        There should only be commands (described above) in this directory. If a command needs more then one class make a helper
        package inside /commands and import from there.

        Returns
        -------
        dict
            Dictionary of command objects. {'command str': command obj, ...}.
        """
        command_dct = {}

        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/commands"
        file_lst = os.listdir(dir_path)

        for file in file_lst:
            if file.endswith(".py") and "__init__" not in file:

                module_name = "assistant4discord.assistant.commands.{}".format(file[:-3])
                module = import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and str(obj.__module__).count(".") == 3:

                        # initialize command
                        obj = obj()

                        # look for method special
                        if obj.special.get("method"):
                            if self.method == obj.special.get("method"):
                                command_dct[name] = obj
                                print("imported command: {}".format(name))
                            else:
                                print("NOT imported command: {}".format(name))
                        else:
                            command_dct[name] = obj
                            print("imported command: {}".format(name))

        print("-------------------------------\nimported {} commands\n".format(len(command_dct)))
        return command_dct

    def get_command_calls(self):
        command_calls = []

        for command in self.commands.values():
            command_calls.append(command.call)

        return command_calls

    def set_master_attributes(self):
        """ Set basic attributes in every command."""

        for command_str, command in self.commands.items():

            command.db = self.db
            command.client = self.client
            command.commands = self.commands
            command.sim = self.sim


class Messenger(Commander):
    """ Class for message -> command mapping. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initializer(self):
        """ Runs once on ready and initializes command that have initialize method.

        Returns
        -------
        List of commands to be initialized (ran once on bot start).
        """
        initialized = []

        for command_str, command in self.commands.items():
            if getattr(command, "initialize", False):
                initialized.append(command)

        return initialized

    def message_to_command(self, message):
        """ Uses message_x_command_sim from assistant4discord/nlp_tasks/ to get the command that matches the most with user input.

        Parameters
        ----------
        message: obj
            https://discordpy.readthedocs.io/en/latest/api.html#message

        Returns
        -------
        Chosen command or None if cosine similarity on all command calls below some value.
        """
        sim_arr = self.sim.message_x_command_sim(message.content)
        picked_command_str = self.calls[int(np.argmax(sim_arr))]

        # print("message:", message.content)
        # for i in sim_arr.argsort()[-3:][::-1]:
        #     print("{}: {:.3f}".format(self.calls[i], sim_arr[i]))

        if np.max(sim_arr) < 0.25:
            return None

        for command in self.commands.values():
            if command.call == picked_command_str:
                command.message = message
                return command
