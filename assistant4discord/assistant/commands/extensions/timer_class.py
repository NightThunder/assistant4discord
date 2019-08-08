from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_local, convert_sec
import time
import numpy as np


class Timer(Master):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        name: str
            Used for identification.
        run_on_init: bool
            If True runs once on initialization.
        use_asyncio: bool
            True because asyncio and aiohttp are needed.
        time_to_message: int
            Seconds to message.
        every: bool
            True if repeated (do again after sleep).
        switch: int
            0 if never ran, 1 if ran once or more.
        future_command: obj
            Class name of command to be executed.
        created_on: int
            When did todo() ran.

        Note
        ----
        All None attributes in __init__ are initialized in todo() method.

        """
        super().__init__(**kwargs)
        self.name = "time_it"
        self.run_on_init = True
        self.use_asyncio = True
        self.time_to_message = None
        self.every = None
        self.switch = 0
        self.future_command = None
        self.created_on = int(time.time())

    async def todo(self):

        if self.switch == 0:
            (self.time_to_message, self.every, future_command_str) = self.message_filter()

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
            else:
                chosen_one.message = self.message

            self.created_on = int(time.time())

            await chosen_one.doit()

    def message_to_command(self, message, calls):
        """ Same as Messenger. """

        sim_arr = self.sim.message_x_command_sim(" ".join(message))
        picked_command_str = calls[int(np.argmax(sim_arr))]

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
        if self.every:
            return "command: {}\nset every {}\nnext run on: {}".format(
                self.future_command,
                convert_sec(self.time_to_message),
                timestamp_to_local(self.time_to_message + self.created_on),
            )
        else:
            return "command: {}\nset for {}".format(
                self.future_command,
                timestamp_to_local(self.time_to_message + self.created_on),
            )
