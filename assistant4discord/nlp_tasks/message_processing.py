import re


def remove_punctuation(sent):
    # punct = r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + '’`”“'    # removes punct
    # text_nopunct = ''.join(char for char in sent if char not in punct)
    text_nopunct = re.sub(r'[\\!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~’”“]+', ' ', sent)    # replaces punct
    return text_nopunct


def replace_numbers(sent):
    text_nonum = re.sub(r'[0-9]+', 'stevilka', sent)
    return text_nonum


def word_by_word(sent):
    tokens = re.split(r'\W+', sent[0])
    tokens_noempty = [word.lower() for word in tokens if word != '']
    return tokens_noempty


def word2vec_input(message, replace_num=True):
    """ Prepares message for word2vec.
    notes:
        sent_tokenize():  splits into sentences,
        a: replaces numbers with stevilka, removes punctuation, replaces /n,
        b: lowers,
        c: splits sentence into words
    Args:
        message: message string
        replace_num: True if you don't want to replace numbers
    Returns: sentences word by word in list [[w1, w2, ...], [w1, w2, ...], ...]
                                              sent1          sent2
    """
    # a = [replace_numbers(remove_punctuation(message)).replace('\n', ' ')]
    # b = [i.lower() for i in a]
    # c = word_by_word(b)
    if replace_num:
        text_in_sent = (word_by_word([i.lower() for i in [replace_numbers(remove_punctuation(message)).replace('\n', ' ')]]))
    else:
        text_in_sent = (word_by_word([i.lower() for i in [remove_punctuation(message).replace('\n', ' ')]]))

    return text_in_sent
