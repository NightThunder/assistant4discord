import re


def remove_punctuation(sent):
    punct = r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + '’`”“'
    text_nopunct = ''.join(char for char in sent if char not in punct)
    return text_nopunct


def replace_numbers(sent):
    text_nonum = re.sub(r'[0-9]+', 'stevilka', sent)
    return text_nonum


def process_message(message):
    return replace_numbers(remove_punctuation(message))
