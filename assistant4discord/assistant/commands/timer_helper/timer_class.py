from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc
import time
import numpy as np


class Timer(Master):
    """ self.time_to_timer, self.every, future_command_str: asyncio.sleep time, if loop, string to compare to commands
        self.future_command: command to run in the future
        self.set_for: d m y format of set timer
        self.task: coro task saver, used in timer.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        (self.time_to_timer, self.every, future_command_str) = self.message_filter()
        self.future_command = self.message_to_command(future_command_str)
        self.set_for = int(self.time_to_timer + time.time())
        self.task = None

    def message_to_command(self, message):
        """ Same as Messenger. """

        sim_arr = self.sim.message_x_command_sim(' '.join(message), self.command_vectors, saved_command_vectors=True)
        picked_command_str = self.calls[int(np.argmax(sim_arr))]

        if np.max(sim_arr) < 0.3:
            return None

        for command in self.commands.values():
            if command.call == picked_command_str:
                command.message = self.message
                return command

    def message_filter(self):
        """ Use sent_time_finder to get time info. Find time in sent and remove it. Assumes that command is after or before 'time'.

            Example: 'time ping 10 sec' -> 'time ping' -> 'ping'
        """

        time_to_command, sent_no_time, every = sent_time_finder(self.message.content[22:], filter_times=True)

        time_i = sent_no_time.index('time')

        if time_i == 0:
            future_command = sent_no_time[time_i:]
        else:
            future_command = sent_no_time[:time_i]

        future_command.pop(time_i)

        return time_to_command, every, future_command

    def __str__(self):
        """ %d.%m.%Y %H:%M:%S representation."""
        if self.every:
            return 'next run set for: {}'.format(timestamp_to_utc(self.set_for))
        else:
            return 'set for: {}'.format(timestamp_to_utc(self.set_for))
