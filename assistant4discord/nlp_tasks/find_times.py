from assistant4discord.nlp_tasks.message_processing import word2vec_input
import datetime
from datetime import date
import time


special_time_words = ['every', 'at', 'tomorrow', 'on']

days_dct = {'monday': 0, 'mon': 0, 'mo': 0, 'tuesday': 1, 'tue': 1, 'tu': 1, 'wednesday': 2, 'wed': 2, 'we': 2,
            'thursday': 3, 'thu': 3, 'th': 3, 'friday': 4, 'fri': 4, 'fr': 4, 'saturday': 5, 'sat': 5, 'sa': 5,
            'sunday': 6, 'sun': 6, 'su': 6}

times_dct = {'second': 1, 'seconds': 1, 'sec': 1, 's': 1, 'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
             'hour': 3600, 'hours': 3600, 'h': 3600, 'day': 86400, 'days': 86400, 'd': 86400, 'week': 604800,
             'weeks': 604800, 'w': 604800, 'tomorrow': 86400}


def sent_time_finder(sent):
    vec_sent = word2vec_input(sent)
    true_sent = word2vec_input(sent, replace_num=False)
    t = 0
    every = False

    for i, s in enumerate(vec_sent):

        if s in times_dct:
            try:
                num = int(true_sent[i - 1])
            except ValueError:
                num = 1

            t += times_dct[s] * num

            if vec_sent[i - 1] == 'every' or vec_sent[i - 2] == 'every':
                every = True

        if s in days_dct:
            today_is = date.today().strftime('%A').lower()

            t = abs(days_dct[s] - days_dct[today_is]) * 86400

            if t == 0:
                t = 7 * 86400

            if vec_sent[i - 1] == 'every':
                every = True

        if s == 'at':
            for j, hms in enumerate(true_sent[i + 1:]):

                if vec_sent[j + i + 1] == 'stevilka':
                    if j == 0:
                        t += int(hms) * 3600
                    elif j == 1:
                        t += int(hms) * 60
                    else:
                        t += int(hms)
                else:
                    break

        if s == 'on':
            d = 0
            m = date.today().strftime('%m')
            y = date.today().strftime('%Y')

            for j, dmy in enumerate(true_sent[i + 1:]):

                if vec_sent[j + i + 1] == 'stevilka':
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

            t += datetime.datetime(y, m, d, 0, 0).timestamp()

    if t - time.time() < 0:
        return None, None
    else:
        return t, every


sent = 'remind me on 17.8.19 at 17:00'

t_, every_ = sent_time_finder(sent)

print(t_, every_)


def timestamp_to_utc(timestamp):
    """timestamp -> utc time
       print(timestamp_to_utc('1576022400'))"""
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y %H:%M:%S')


print(timestamp_to_utc(t_))
