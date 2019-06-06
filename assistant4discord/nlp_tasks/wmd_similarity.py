from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
import os


def get_similarity(message, command):
    distance = wv_model.wmdistance(message, command)
    return distance


def load_model(file_name):
    path = get_tmpfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name))

    if file_name[-3:] == '.kv':
        return KeyedVectors.load(path, mmap='r')
    else:
        return Word2Vec.load(path)


wv_model = load_model('5days_askreddit_model.kv')
