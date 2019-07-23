from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from assistant4discord.nlp_tasks.message_processing import replace_numbers


class tfSimilarity:
    """ Term frequency class.

    References
    ----------
    http://blog.christianperone.com/2013/09/machine-learning-cosine-similarity-for-vector-space-models-part-iii/
    https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
    """

    def __init__(self, test_set):
        self.vectorizer = None
        self.tf_matrix = self.get_tf_matrix(test_set)

    def get_tf_matrix(self, test_set):
        """ Make term frequency matrix from calls.

        Note
        -------
        Get vocab: vectorizer.vocabulary_
        """
        self.vectorizer = CountVectorizer()

        tf_matrix = self.vectorizer.fit_transform(test_set).toarray()

        return self.normalize_to_1(tf_matrix)

    def get_train_vec(self, train_set):
        """ Make term frequency vector from message."""
        train_vec = self.vectorizer.transform(train_set).toarray()

        return self.normalize_to_1(train_vec)

    def message_x_command_sim(self, message):
        """Return cosine similarity of vector and matrix rows."""
        return cosine_similarity(
            self.get_train_vec([replace_numbers(message)]), self.tf_matrix).ravel()

    @staticmethod
    def normalize_to_1(mat):
        """ Replace all values > 1 with 1."""
        mat[mat > 1] = 1
        return mat
