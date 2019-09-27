import re


def remove_punctuation(sent):
    text_nopunct = re.sub(r'[\\!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~’”“]+', " ", sent)
    return text_nopunct


def replace_numbers(sent):
    # Note: all ints and floats in vector model were replaced by string 'stevilka'
    text_nonum = re.sub(r"[0-9]+", "stevilka", sent)
    return text_nonum


def word_by_word(sent):
    tokens = re.split(r"\W+", sent[0])
    tokens_noempty = [word.lower() for word in tokens if word != ""]
    return tokens_noempty


def word2vec_input(message, replace_num=True):
    """ Prepares message for word2vec. Sentence -> list of words in sentence.

    sent_tokenize():  splits into sentences (not used here)
    a: replaces numbers with "stevilka", removes punctuation, replaces /n,
    b: lowers,
    c: splits sentence into words

    a = [replace_numbers(remove_punctuation(message)).replace('\n', ' ')]
    b = [i.lower() for i in a]
    c = word_by_word(b)

    Parameters
    ----------
    message: str
        Discord message.
    replace_num: bool, optional
        If True replaces all ints and floats to string "stevilka".

    Returns
    -------
    list of strings
        [word_1, word_2, ..., word_n]
    """
    if replace_num:
        text_in_sent = (word_by_word([i.lower() for i in [replace_numbers(remove_punctuation(message)).replace('\n', ' ')]]))
    else:
        text_in_sent = (word_by_word([i.lower() for i in [remove_punctuation(message).replace('\n', ' ')]]))

    return text_in_sent
