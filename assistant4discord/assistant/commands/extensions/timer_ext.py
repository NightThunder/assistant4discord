import time
import numpy as np
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_local, convert_sec
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.helpers.extend import Extend, ExtError


class Timer(Extend):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        future_command: obj
            Class name of command to be executed.

        """
        super().__init__(**kwargs)
        self.name = "time_it"
        self.use_asyncio = True
        self.future_command = None

    async def doit(self):

        if self.switch == 0:
            (self.time_to_message, self.every, future_command_str) = self.get_message()

            calls = self.get_command_calls()
            future_command_call = self.message_to_command(future_command_str, calls)

            if not future_command_call:
                return None

            for command_str, command in self.commands.items():
                if command.call == future_command_call:
                    self.future_command = command_str

            self.switch += 1

        else:
            chosen_one = self.commands[self.future_command]

            if self.saved_channel:
                chosen_one.saved_channel = self.saved_channel
                chosen_one.ch_type = self.ch_type
            else:
                chosen_one.message = self.message

            self.created_on = int(time.time())

            await chosen_one.doit()

            return None

    def message_to_command(self, message, calls):
        """ Same as Messenger. """

        sim_arr = self.sim.message_x_command_sim(" ".join(message))
        picked_command_str = calls[int(np.argmax(sim_arr))]

        if np.max(sim_arr) < 0.25:
            raise ExtError("No command found!")

        return picked_command_str

    def get_command_calls(self):
        command_calls = []

        for command_str, command in self.commands.items():
            command_calls.append(command.call)

        return command_calls

    def get_message(self):
        """ Get time and command from messsage.

        Use sent_time_finder to get time info. Find time in sent and remove it.

        """
        time_to_command, every = sent_time_finder(self.message.content)

        future_command = word2vec_input(self.message.content)

        time_i = future_command.index("time")
        future_command.pop(time_i)

        return time_to_command, every, future_command

    def __str__(self):
        if self.every:
            return "command: {}\nset every {}\nnext run on {}".format(
                self.future_command,
                convert_sec(self.every),
                timestamp_to_local(self.time_to_message + self.created_on),
            )
        else:
            return "command: {}\nset for {}".format(
                self.future_command,
                timestamp_to_local(self.time_to_message + self.created_on),
            )
