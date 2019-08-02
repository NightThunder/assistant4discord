from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc
import time
import numpy as np


class Timer(Master):
    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        calls: list of str
            Get command calls from all commands.
        time_to_message: int
        every: bool
        future_command_str: str
            User message with command and time in it.
        created_on: int
            When was this initialized
        """
        super().__init__(**kwargs)
        self.name = 'timers'
        self.run_on_init = True
        self.use_asyncio = True
        self.calls = None
        self.time_to_message = None
        self.every = None
        self.future_command_call = None
        self.created_on = int(time.time())

    def todo(self):
        self.calls = self.get_command_calls()
        (self.time_to_message, self.every, future_command_str) = self.message_filter()
        self.future_command_call = self.message_to_command(future_command_str)

    def message_to_command(self, message):
        """ Same as Messenger. """

        sim_arr = self.sim.message_x_command_sim(" ".join(message))
        picked_command_str = self.calls[int(np.argmax(sim_arr))]

        if np.max(sim_arr) < 0.25:
            return None

        return picked_command_str

    def get_command_calls(self):
        command_calls = []

        for command_str, command in self.commands.items():
            command_calls.append(command.call)

        return command_calls

    def message_filter(self):
        """ Get time and command from messsage.

        Use sent_time_finder to get time info. Find time in sent and remove it. Assumes that command is after or before 'time'.

        Examples
        --------
        'time ping 10 sec' -> 'time ping' -> 'ping'
        """

        time_to_command, sent_no_time, every = sent_time_finder(self.message.content, filter_times=True)

        time_i = sent_no_time.index("time")

        if time_i == 0:
            future_command = sent_no_time[time_i:]
        else:
            future_command = sent_no_time[:time_i]

        future_command.pop(time_i)

        return time_to_command, every, future_command

    def __str__(self):
        """ %d.%m.%Y %H:%M:%S representation."""
        if self.every:
            return "command: {}\nnext run set for {}".format(
                self.message.content,
                timestamp_to_utc(self.time_to_message + self.created_on),
            )
        else:
            return "command: {}\nset for {}".format(
                self.message.content,
                timestamp_to_utc(self.time_to_message + self.created_on),
            )
