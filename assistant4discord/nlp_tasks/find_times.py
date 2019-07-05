from assistant4discord.nlp_tasks.message_processing import word2vec_input
import datetime
from datetime import date
import time


special_time_words = ['every', 'at', 'tomorrow', 'on']

times_dct = {'second': 1, 'seconds': 1, 'sec': 1, 's': 1, 'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
             'hour': 3600, 'hours': 3600, 'h': 3600, 'day': 86400, 'days': 86400, 'd': 86400, 'week': 604800,
             'weeks': 604800, 'w': 604800, 'tomorrow': 86400}

days_dct = {'monday': 0, 'mon': 0, 'mo': 0, 'tuesday': 1, 'tue': 1, 'tu': 1, 'wednesday': 2, 'wed': 2, 'we': 2,
            'thursday': 3, 'thu': 3, 'th': 3, 'friday': 4, 'fri': 4, 'fr': 4, 'saturday': 5, 'sat': 5, 'sa': 5,
            'sunday': 6, 'sun': 6, 'su': 6}


def sent_time_finder(sent, filter_times=False):
    """ Simple time lookup from string.
        (1) Looks for times_dct keys in sent. If found checks if int before key.
            If int not found set num = 1 else set num = int. Multiply num by key's value. Check for 'every''
        (2) Same as (1) but for days_dct.
        (3) If word 'at' in sent assume 00:00:00 time format follows (can be 00 or 00:00 or 00:00:00).
        (4) If word 'on' in sent assume specific date follows in format d m y.

    Example: sent = 'remind me on 17.8.19 at 17:00' -> (3796550, False)
             sent = 'remind me every day' -> (86400, True)

    Args:
        sent: sentence == string
        filter_times: if True return word2vec_input list with no time words

    Returns: (int for time in string, word2vec_input list with no times, True if every in string). Returns time TO event.

    Not implemented: months, years

    """
    vec_sent = word2vec_input(sent)
    true_sent = word2vec_input(sent, replace_num=False)
    t = 0
    every = False
    index_time = []

    for i, w in enumerate(vec_sent):

        if w in times_dct:
            try:
                num = int(true_sent[i - 1])
                index_time.append(i - 1)
            except ValueError:
                num = 1

            t += times_dct[w] * num
            index_time.append(i)

            if vec_sent[i - 1] == 'every' or vec_sent[i - 2] == 'every':
                if vec_sent[i - 1] == 'every':
                    index_time.append(i - 1)
                else:
                    index_time.append(i - 2)
                every = True

        elif w in days_dct:
            today_is = date.today().strftime('%A').lower()

            t = abs(days_dct[w] - days_dct[today_is]) * 86400

            if t == 0:
                t = 7 * 86400

            index_time.append(i)

            if vec_sent[i - 1] == 'every':
                index_time.append(i - 1)
                every = True

        elif w == 'at':
            for j, hms in enumerate(true_sent[i + 1:]):

                if vec_sent[j + i + 1] == 'stevilka':

                    index_time.append(j + i + 1)

                    if j == 0:
                        t += int(hms) * 3600
                    elif j == 1:
                        t += int(hms) * 60
                    else:
                        t += int(hms)
                else:
                    break

        elif w == 'on':
            d = 0
            m = date.today().strftime('%m')
            y = date.today().strftime('%Y')

            for j, dmy in enumerate(true_sent[i + 1:]):

                if vec_sent[j + i + 1] == 'stevilka':

                    index_time.append(j + i + 1)

                    if j == 0:
                        d = int(dmy)
                    elif j == 1:
                        m = int(dmy)
                    else:
                        if len(dmy) == 2:
                            y = int(dmy) + 2000
                        else:
                            y = int(dmy)
                else:
                    break

            t += int(datetime.datetime(y, m, d, 0, 0).timestamp() - time.time())

        else:
            continue

    if filter_times:
        return t, sent_no_time(vec_sent, index_time), every
    else:
        return t, every


def sent_no_time(vec_sent, ind):
    """ Cleans time words and time numbers from sentence.

    Args:
        vec_sent: word2vec_input of sentence
        ind: index values of time words and corresponding numbers

    Returns: word2vec_input list of sentence with no time words and no time numbers

    """

    no_time_vec_sent = []

    for i, w in enumerate(vec_sent):
        if i not in ind:
            no_time_vec_sent.append(w)

    return no_time_vec_sent


def timestamp_to_utc(timestamp):
    """timestamp -> utc time
       example: timestamp_to_utc(1576022400) -> '11.12.2019 01:00:00' """
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y @ %H:%M:%S')
