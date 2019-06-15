import asyncio
from assistant4discord.nlp_tasks.message_processing import word2vec_input


class Master:

    def __init__(self, client=None, message=None, similarity=None):
        """ Base class for commands.

        Args:
            client: discord client object
            message: discord message object
            similarity: Similarity object from assistant4discord.nlp_tasks.similarity
        """
        self.client = client
        self.message = message
        self.sim = similarity


class Help(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'help'
        self.commands = None

    async def doit(self):

        message = self.message.content[22:]

        if len(word2vec_input(message)) > 1:
            for i, (command_str, command) in enumerate(self.commands.items()):
                if command_str in message.lower() and command_str != 'help':
                    await self.message.channel.send(command.help)
                    break

                if i == len(self.commands) - 1:
                    await self.message.channel.send('Command not found!')

        else:
            command_str = 'My commands: '
            for i, command_str_ in enumerate(self.commands.keys()):
                if i < len(self.commands) - 1:
                    command_str += command_str_.lower() + ', '
                else:
                    command_str += command_str_.lower()

            command_str += '\nType help <command> for more info!'

            await self.message.channel.send(command_str)


class Ping(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'ping'
        self.help = 'Ping discord server and return response time in ms.'

    async def doit(self):
        await self.message.channel.send('{} ms'.format(round(self.client.latency * 1000)))


class After10(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'sleep'
        self.help = 'asyncio.sleep() test'

    async def doit(self):
        await self.message.channel.send('sleeping for 10')
        await asyncio.sleep(10)
        await self.message.channel.send('woken up after 10')


class Word2WordSim(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'similarity'
        self.help = 'Returns cosine similarity between last two words in message.\nNote: only works with keyword similarity.'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        similarity = self.sim.model.similarity(sent[-1], sent[-2])

        await self.message.channel.send(str(similarity))


class MostSimilarWords(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'most similar'
        self.help = 'Return 50 most similar words to last word in message.\nNote: only works with keyword most similar.'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        sims = self.sim.model.similar_by_word(sent[-1], topn=50)

        sim_str = ''
        for i in sims:
            sim_str += '{}: {:.2f} '.format(i[0], i[1])

        await self.message.channel.send(sim_str)
