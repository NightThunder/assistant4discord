from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.message_processing import word2vec_input


class Word2WordSim(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'similarity'
        self.help = '```***Word2wordSim help***\n' \
                    'Return cosine similarity between last two words in message.\n' \
                    'Example: similarity <word1>, <word2>\n' \
                    'Note: only works with keyword "similarity".```'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        similarity = self.sim.model.similarity(sent[-1], sent[-2])

        await self.message.channel.send(str(similarity))


class MostSimilarWords(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'most similar'
        self.help = '```***MostSimilarWords help***\n' \
                    'Return 50 most similar words to last word in message.\n' \
                    'Example: similar <word>\n' \
                    'Note: only works with keyword "similar".```'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        sims = self.sim.model.similar_by_word(sent[-1], topn=50)

        sim_str = ''
        for i in sims:
            sim_str += '{}: {:.2f} '.format(i[0], i[1])

        await self.message.channel.send(sim_str)


class WordNum(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'number'
        self.help = '```***WordNum help***\n' \
                    'How many times does a word appear in vector model.\n' \
                    'Example: number <word>\n' \
                    'Note: all words 10+ as set by model. Numbers replaced by stevilka.```'

    async def doit(self):
        sent = word2vec_input(self.message.content[22:])
        num = self.sim.model.vocab[sent[-1]].count
        await self.message.channel.send(str(num))
