import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input
from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.timer_helper.timer_class import Timer


class TimeIt(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'time stevilka time'
        self.help = '```***Timer help***\n' \
                    'Run a command in specified time.\n' \
                    'Example: time <time when to run> <any command>```'
        self.all_timers = []

    def remove_dead_timers(self):

        all_active_timers = []

        for timer in self.all_timers:
            if not timer.task.done():
                all_active_timers.append(timer)

        self.all_timers = all_active_timers

    async def coro_doit(self, timer):

        await self.message.channel.send('{} {}'.format(timer.future_command.__class__.__name__, str(timer)))

        while True:
            await asyncio.sleep(timer.time_to_timer)
            await timer.future_command.doit()

            if timer.every is False:
                return

    async def doit(self):

        timer = Timer(message=self.message, similarity=self.sim, commands=self.commands, command_vectors=self.command_vectors, calls=self.calls)

        if timer.time_to_timer and timer.future_command:
            task = self.client.loop.create_task(self.coro_doit(timer))
            timer.task = task
            self.all_timers.append(timer)
        else:
            await self.message.channel.send('something went wrong')


class ShowTimers(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'show timer'
        self.help = '```***ShowTimers help***\n' \
                    'Display user\'s active timers.\n```'

    async def doit(self):

        self.commands['TimeIt'].remove_dead_timers()

        all_timers = self.commands['TimeIt'].all_timers
        timer_str = ''
        n_timers = 0
        for i, timer in enumerate(all_timers):
            if timer.message.author == self.message.author and not timer.task.done():
                timer_str += '**timer {}:** {} {}\n'.format(i, timer.future_command.__class__.__name__, str(timer))

                if i != len(all_timers) - 1:
                    timer_str += '--------------------\n'

                n_timers += 1

        if n_timers != 0:
            await self.message.channel.send(timer_str)
        else:
            await self.message.channel.send('You have no active timers!')


class KillTimer(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'kill timer stevilka'
        self.help = '```***KillTimer help***\n' \
                    'Cancels user\'s active timer.\n' \
                    'Example: cancel timer <timer\'s number shown in ShowTimers>```'

    async def doit(self):

        self.commands['TimeIt'].remove_dead_timers()

        try:
            to_kill = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong')
            return

        n_timers = 0
        for i, timer in enumerate(self.commands['TimeIt'].all_timers):
            if timer.message.author == self.message.author and not timer.task.done() and i == to_kill:
                timer.task.cancel()
                break
            else:
                n_timers += 1

        if to_kill > n_timers:
            await self.message.channel.send('Could not find that timer!')
        else:
            await self.message.channel.send('Timer {} canceled!'.format(to_kill))
