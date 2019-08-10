from assistant4discord.nlp_tasks.message_processing import word2vec_input
import datetime
from datetime import date
import time


times_dct = {
    "second": 1,
    "seconds": 1,
    "sec": 1,
    "s": 1,
    "minute": 60,
    "minutes": 60,
    "min": 60,
    "m": 60,
    "hour": 3600,
    "hours": 3600,
    "h": 3600,
    "day": 86400,
    "days": 86400,
    "d": 86400,
    "week": 604800,
    "weeks": 604800,
    "w": 604800,
    "tomorrow": 86400,
}

days_dct = {
    "monday": 0,
    "mon": 0,
    "mo": 0,
    "tuesday": 1,
    "tue": 1,
    "tu": 1,
    "wednesday": 2,
    "wed": 2,
    "we": 2,
    "thursday": 3,
    "thu": 3,
    "th": 3,
    "friday": 4,
    "fri": 4,
    "fr": 4,
    "saturday": 5,
    "sat": 5,
    "sa": 5,
    "sunday": 6,
    "sun": 6,
    "su": 6,
}


def sent_time_finder(sent):
    """ Simple time lookup from string.

    (1) Looks for times_dct keys in sent. If found checks if int before key.
    If int not found set num = 1 else set num = int. Multiply num by key's value. Check for 'every'.
    (2) Same as (1) but for days_dct.
    (3) If word 'at' in sent assume 00:00:00 time format follows (can be 00 or 00:00 or 00:00:00).
    (4) If word 'on' in sent assume specific date follows in format d m y.

    Parameters
    ----------
    sent: str
        Discord message.

    Returns
    -------
    Returns time TO event.
    if filter_times:
        (int for time in string, word2vec_input list with no times, True if every in string else False)
    else:
        (int for time in string, True if every in string else False)

    Note
    ----
    Naive (bad) implementation. Timezones not supported, works with local only.

    Examples
    --------
    sent = 'remind me on 17.8.19 at 17:00' -> (3796550, False)
    sent = 'remind me every day' -> (86400, True)

    """
    vec_sent = word2vec_input(sent)
    true_sent = word2vec_input(sent, replace_num=False)

    t = 0
    now = datetime.datetime.now()

    in_sent = whats_in_sent(true_sent)

    if 'every' in true_sent:
        every = True
    else:
        every = False

    for i, w in enumerate(vec_sent):

        if w in times_dct:
            try:
                num = int(true_sent[i - 1])
            except ValueError:
                num = 1

            t += times_dct[w] * num

            if w == 'tomorrow':
                t -= now.hour * 3600 + now.minute * 60 + now.second

        elif w in days_dct:
            today_is = date.today().strftime("%A").lower()

            day_diff = days_dct[w] - days_dct[today_is]

            if day_diff < 0:
                day_diff = 7 - abs(day_diff)

            t = day_diff * 86400 - (now.hour * 3600 + now.minute * 60 + now.second)

            if t < 0:
                t = 7 * 86400 - (now.hour * 3600 + now.minute * 60 + now.second)

        elif w == "at":

            if "on" not in true_sent and 'day' not in in_sent:
                to_midnight = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)

                if 'tomorrow' in true_sent:
                    t = 0

                t += to_midnight

            for j, hms in enumerate(true_sent[i + 1:]):

                if vec_sent[j + i + 1] == "stevilka":

                    if j == 0:
                        t += int(hms) * 3600
                    elif j == 1:
                        t += int(hms) * 60
                    else:
                        t += int(hms)

                else:
                    break

        elif w == "on":

            # check if on before day word (if True this is not it and pass)
            if 'day' not in in_sent:
                d = 0
                m = now.month
                y = now.year

                for j, dmy in enumerate(true_sent[i + 1:]):

                    if vec_sent[j + i + 1] == "stevilka":

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

                t += int(datetime.datetime(y, m, d, 0, 0).timestamp() - time.time()) + 1
            else:
                pass

        else:
            continue

    return t, every


def whats_in_sent(true_sent):

    in_sent = []

    for word_ in true_sent:
        for time_ in times_dct:
            if word_ == time_:
                in_sent.append('time')

        for day_ in days_dct:
            if word_ == day_:
                in_sent.append('day')

        if word_ == 'on':
            in_sent.append('on')
        elif word_ == 'at':
            in_sent.append('at')
        else:
            pass

    return in_sent


def timestamp_to_local(timestamp):
    """ timestamp -> local time

    Parameters
    ----------
    timestamp: float or int
        https://www.unixtimestamp.com/

    Returns
    -------
    str
        %d.%m.%Y @ %H:%M:%S
    """
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%d.%m.%Y @ %H:%M:%S")


def convert_sec(seconds):
    """ Converts seconds to w d h m s.

    Parameters
    ----------
    seconds: int

    Returns
    -------
    x weeks, x days, x h, x min, x sec

    References
    ----------
    https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days
    """
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('h', 3600),
        ('min', 60),
        ('sec', 1),
        )

    result = []

    for name, count in intervals:
        value = seconds // count

        if value:
            seconds -= value * count

            if value == 1:
                name = name.rstrip('s')

            result.append("{} {}".format(value, name))

    return ', '.join(result)


# ex1 = ['tomorrow', 'tomorrow at 12', '1 day', '2 days at 22:00', 'fri', 'mon', 'sat at 9', '10 sec', '1 week']
# for e in ex1:
#     print(e)
#     _ = sent_time_finder(e)[0]
#     print(timestamp_to_local(_ + time.time()))
#     print('-----------------------------')
