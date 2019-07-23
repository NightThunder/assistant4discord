from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math


# this is needed so that commands that use calls from different commands don't get mixed up
boosted = {"similar": 1000, "similarity": 1000, "help": 10, "number": 10, "time": 100}


class w2vSimilarity:
    def __init__(self, model_name, test_set):
        """
        Parameters
        ----------
        model_name: str
        test_set: list of str
            Command calls.

        Other Parameters
        ----------------
        model: obj
        w2v_matrix: np.ndarray()
            Sentence vectors made from command calls. Initialized on start.
        """
        self.model = self.load_model(model_name)
        self.w2v_matrix = self.get_sentence2vec(test_set)

    @staticmethod
    def load_model(file_name):
        """ Loads w2v model with gensim.

        References
        ----------
        https://radimrehurek.com/gensim/models/word2vec.html
        https://rare-technologies.com/word2vec-tutorial/
        https://radimrehurek.com/gensim/models/keyedvectors.html#module-gensim.models.keyedvectors

        Raises
        ------
        ValueError
            If no model found.
        """
        path = get_tmpfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../data/models/" + file_name))

        if file_name[-3:] == ".kv":
            return KeyedVectors.load(path, mmap="r")
        elif file_name[-6:] == ".model":
            return Word2Vec.load(path)
        else:
            raise ValueError("no model found")

    def sentence2vec(self, content):
        """ Basic vector sentence representation.
        
        Each word is represented by a n-dimensional vector (n=300). Sentence2vec sums all word vectors in a sentence
        dividing each by it's weight.
        
        Parameters
        ----------
        content: list or list of lists
            List if single sentence or list of lists if "matrix" of sentences. List of lists only once on initialization.
        
        Note
        ----
        Uses log weight for each word.
        
        Returns
        -------
        np.ndarray()
            Matrix of sentence vectors.
        """
        m = len(content)
        n = self.model.vector_size
        is_message = False

        if any(isinstance(el, list) for el in content) is False:
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
        """ Calls sentence2vec. Different for string or list of strings."""

        if type(content) is list:
            commands = [word2vec_input(i) for i in content]
            return self.sentence2vec(commands)
        else:
            message = word2vec_input(content)
            return self.sentence2vec(message)

    @staticmethod
    def sentence_sim(sentence, compare_to_sentences):
        """ Return cosine similarity of vector and matrix rows."""

        return cosine_similarity(sentence, compare_to_sentences).ravel()

    def message_x_command_sim(self, message):
        """ Compares message to sentence vectors.

        Parameters
        ----------
        message: str
            Discord message.

        Returns
        -------
        np.ndarray()
            Vector of cosine similarities.
        """
        return self.sentence_sim(self.get_sentence2vec(message), self.w2v_matrix)
