from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math


boosted = {'similar': 1000, 'similarity': 1000, 'help': 10, 'number': 10}


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

    def sentence2vec(self, content):
        post_vec_lst = []
        size = self.model.vector_size
        is_message = False

        if any(isinstance(el, list) for el in content) is False:
            is_message = True
            content = [content]

        for sent in content:

            sum_post = np.zeros(size)

            for word in sent:
                try:
                    if word in boosted and is_message:
                        weight = boosted[word] / (1 + math.log(self.model.vocab[word].count))
                    else:
                        weight = 1 / (1 + math.log(self.model.vocab[word].count))

                    sum_post += self.model[word] * weight

                except KeyError:
                    sum_post += np.zeros(size)

            post_vec_lst.append(sum_post)

        post_mat = np.array(post_vec_lst)

        return post_mat

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

    def message_x_command_sim(self, message: str, commands: list, saved_command_vectors=False):
        """ Compares message to list of commands or to sentence vectors.

        Args:
            message: string
            commands: list of text commands or command sentence vectors if saved_command_vectors=True
            saved_command_vectors: set True if already calculated vector commands (at start or in .pickle)

        Returns: np.array of cosine similarities
        """
        if saved_command_vectors:
            return self.sentence_sim(self.get_sentence2vec(message), commands)
        else:
            return self.sentence_sim(self.get_sentence2vec(message), self.get_sentence2vec(commands))
