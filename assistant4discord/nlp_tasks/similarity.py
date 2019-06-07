from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Similarity:

    def __init__(self, model_name):
        self.model = self.load_model(model_name)

    @staticmethod
    def load_model(file_name):
        path = get_tmpfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/models/' + file_name))

        if file_name[-3:] == '.kv':
            return KeyedVectors.load(path, mmap='r')
        elif file_name[-6:] == '.model':
            return Word2Vec.load(path)
        else:
            raise ValueError('no model found')

    def sentence2vec(self, content, a=100):
        post_vec_lst = []
        size = self.model.vector_size

        if any(isinstance(el, list) for el in content) is False:
            content = [content]

        for sent in content:

            sum_post = np.zeros(size)

            for word in sent:
                try:
                    weight = a / (a + self.model.vocab[word].count)
                    sum_post += self.model[word] * weight
                except KeyError:
                    sum_post += np.zeros(size)

            post_vec_lst.append(sum_post)

        post_mat = np.array(post_vec_lst)

        return post_mat

    def sentence_sim(self, sentence, sentence_lst):
        compare_vec = self.sentence2vec(sentence)
        compare_with_vec = self.sentence2vec(sentence_lst)

        return cosine_similarity(compare_vec, compare_with_vec).ravel()

    def message_x_command_sim(self, message: str, commands: list):
        message = word2vec_input(message)
        commands = [word2vec_input(i) for i in commands]

        return self.sentence_sim(message, commands)


# sim = Similarity('5days_askreddit_model.kv').message_x_command_sim('ping this please', ['whats my ping', 'remind me', 'google this'])
# print(sim)
