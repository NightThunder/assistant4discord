from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
import datetime
import time
import numpy as np


times = {'second': 1, 'seconds': 1, 'sec': 1, 's': 1, 'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
         'hour': 3600, 'hours': 3600, 'h': 3600, 'day': 86400, 'days': 86400, 'd': 86400, 'week': 604800,
         'weeks': 604800, 'w': 604800}


class Timer(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.every = self.every_t()
        (self.time_to_timer, self.time_str, future_command_str) = self.message_filter()
        self.future_command = self.message_to_command(future_command_str)
        self.task = None

    def message_to_command(self, message):

        sim_arr = self.sim.message_x_command_sim(' '.join(message), self.command_vectors, saved_command_vectors=True)
        picked_command_str = self.calls[int(np.argmax(sim_arr))]

        # print('message:', ' '.join(message))
        # for i in range(len(self.calls)):
        #     print('{}: {:.2f}'.format(self.calls[i], sim_arr[i]))

        if np.max(sim_arr) < 0.3:
            return None

        for command in self.commands.values():
            if command.call == picked_command_str:
                command.message = self.message
                return command

    def message_filter(self):

        message = word2vec_input(self.message.content[22:], replace_num=False)

        if self.every:
            message.remove('every')

        future_command_str = message.copy()
        str_time_to_command = []

        try:
            time_i = message.index('time')
            future_command_str.pop(time_i)
        except ValueError:
            return

        time_to_command = 0
        for i, word in enumerate(message[time_i:]):

            if word in times:
                try:
                    time_to_command += times[word] * int(message[i + time_i - 1])
                    for _ in range(2):
                        t_str = future_command_str.pop(i + time_i - (len(message) - len(future_command_str)))
                        str_time_to_command.append(t_str)

                    str_time_to_command[-1], str_time_to_command[-2] = str_time_to_command[-2], str_time_to_command[-1]

                except ValueError:
                    return None

                try:
                    message[i + time_i + 2]
                except IndexError:
                    break

                if message[i + time_i + 2] not in times:
                    break

        if time_to_command == 0:
            return None
        else:
            return time_to_command, str_time_to_command, future_command_str

    def every_t(self):
        message = word2vec_input(self.message.content[22:], replace_num=False)
        if 'every' in message:
            return True
        else:
            return False

    def __str__(self):
        if self.every:
            return 'set for every: {}'.format(' '.join(self.time_str))
        else:
            return 'set for: {}'.format(datetime.datetime.fromtimestamp(int(time.time() + self.time_to_timer)).strftime('%d/%m/%Y @ %H:%M:%S'))
