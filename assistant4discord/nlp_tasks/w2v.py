from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math


boosted = {'similar': 1000, 'similarity': 1000, 'help': 10, 'number': 10, 'time': 100}
# this is needed so that commands that use calls from different commands don't get mixed up


class w2vSimilarity:

    def __init__(self, model_name, test_set):
        self.model = self.load_model(model_name)
        self.w2v_matrix = self.get_sentence2vec(test_set)

    @staticmethod
    def load_model(file_name):
        path = get_tmpfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/models/' + file_name))

        if file_name[-3:] == '.kv':
            return KeyedVectors.load(path, mmap='r')
        elif file_name[-6:] == '.model':
            return Word2Vec.load(path)
        else:
            raise ValueError('no model found')

    def sentence2vec(self, content):
        """ Basic vector sentence representation.

            Notes: uses log weight for each word
        """
        m = len(content)
        n = self.model.vector_size
        is_message = False          # check for boosted

        if any(isinstance(el, list) for el in content) is False:        # check if not list of lists
            is_message = True
            m = len(content)
            content = [content]

        sent_mat = np.zeros((m, n))

        for i, sent in enumerate(content):

            sum_post = np.zeros(n)

            for word in sent:
                try:
                    if word in boosted and is_message:
                        weight = boosted[word] / (1 + math.log(self.model.vocab[word].count))
                    else:
                        weight = 1 / (1 + math.log(self.model.vocab[word].count))

                    sum_post += self.model[word] * weight

                except KeyError:
                    pass

            sent_mat[i] = sum_post

        return sent_mat

    def get_sentence2vec(self, content):
        """Calls sentence2vec. Different for string or list of strings."""

        if type(content) is list:
            commands = [word2vec_input(i) for i in content]
            return self.sentence2vec(commands)
        else:
            message = word2vec_input(content)
            return self.sentence2vec(message)

    def sentence_sim(self, sentence, compare_to_sentences):
        """Return cosine similarity of vector and matrix rows."""
        return cosine_similarity(sentence, compare_to_sentences).ravel()

    def message_x_command_sim(self, message: str):
        """ Compares message to sentence vectors.

        Args:
            message: string

        Returns: np.array of cosine similarities
        """
        return self.sentence_sim(self.get_sentence2vec(message), self.w2v_matrix)
