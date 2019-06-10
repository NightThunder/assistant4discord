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
        is_message = False

        if any(isinstance(el, list) for el in content) is False:
            is_message = True
            content = [content]

        for sent in content:

            sum_post = np.zeros(size)

            for word in sent:
                try:
                    if word == 'similarity' and is_message:     # boost
                        print('boosted similarity')
                        weight = 10
                    else:
                        weight = a / (a + self.model.vocab[word].count)

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


# sim = Similarity('5days_askreddit_model.kv').message_x_command_sim('ping this please', ['whats my ping', 'remind me', 'google this'])
# print(sim)


# boost test:
# no boost
# command calls: ['sleep', 'ping', 'word similarity']
# ping ping similarities: [0.07154188 0.96800114 0.27384004]
# ping latency similarities: [0.08508781 0.79037144 0.51513806]
# latency dog similarities: [0.0672977  0.0706988  0.80236408]
# dof cat similarities: [0.06806762 0.05546356 0.9646198 ]

# boost = 10
#    similarities: [0.02809924 0.29108114 0.95242851]
#    similarities: [0.02339426 0.15993421 0.9762784 ]
#    similarities: [0.01550973 0.02204722 0.98508616]
#    similarities: [0.01314699 0.01847625 0.9878561 ]
