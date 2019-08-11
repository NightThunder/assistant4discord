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

    (0) Set time to 0. Check what's in sentence. Look for 'every'. Loop over all words in sentence.
    (1) Looks for times_dct keys in sent. If found checks if int before key.
    If int not found set num = 1 else set num = int. Multiply num by key's value.
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
        (t, every)
        (int for time in string, False or int)
        Returned int in t variable is time to first message.
        Returned int in every variable is time to next message

    Note
    ----
    Naive (bad) implementation. Timezones not supported, works with local time only.

    Examples
    --------
    now time: 11.08.2019 (sun) @ 20:33:37

    string: tomorrow
    date: 12.08.2019 @ 00:00:00
    time to: 3 h, 26 min, 23 sec
    -----------------------------
    string: tomorrow at 12
    date: 12.08.2019 @ 12:00:00
    time to: 15 h, 26 min, 23 sec
    -----------------------------
    string: 1 day
    date: 12.08.2019 @ 20:33:37
    time to: 1 day
    -----------------------------
    string: 2 days at 22:00
    date: 14.08.2019 @ 22:00:00
    time to: 3 days, 1 h, 26 min, 23 sec
    -----------------------------
    string: fri
    date: 16.08.2019 @ 00:00:00
    time to: 4 days, 3 h, 26 min, 23 sec
    -----------------------------
    string: mon
    date: 12.08.2019 @ 00:00:00
    time to: 3 h, 26 min, 23 sec
    -----------------------------
    string: sat at 9
    date: 17.08.2019 @ 09:00:00
    time to: 5 days, 12 h, 26 min, 23 sec
    -----------------------------
    string: 10 sec
    date: 11.08.2019 @ 20:33:47
    time to: 10 sec
    -----------------------------
    string: 1 week
    date: 18.08.2019 @ 20:33:37
    time to: 1 week
    -----------------------------
    string: at 23:50
    date: 11.08.2019 @ 23:50:00
    time to: 3 h, 16 min, 23 sec
    -----------------------------
    string: every day at 22
    date: 12.08.2019 @ 22:00:00
    time to: 1 day, 1 h, 26 min, 23 sec
    -----------------------------
    string: every 2 days at 14
    date: 13.08.2019 @ 14:00:00
    time to: 1 day, 17 h, 26 min, 23 sec
    -----------------------------
    string: every week at 7
    date: 18.08.2019 @ 07:00:00
    time to: 6 days, 10 h, 26 min, 23 sec
    -----------------------------
    string: every 10 h
    date: 12.08.2019 @ 06:33:37
    time to: 10 h
    -----------------------------
    string: every day
    date: 12.08.2019 @ 20:33:37
    time to: 1 day

    """
    vec_sent = word2vec_input(sent)
    true_sent = word2vec_input(sent, replace_num=False)

    t = 0
    now = datetime.datetime.now()

    in_sent = whats_in_sent(true_sent)

    if "every" in true_sent:
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

            if w == "tomorrow":
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

            if every:
                every = t

            if "tomorrow" in true_sent:
                t = 0
                t += 86400 - (now.hour * 3600 + now.minute * 60 + now.second)

            if (
                in_sent["time"] in ["day", "days", "d", "week", "weeks", "w"]
                and in_sent["on"] is False
            ):
                t += 86400 - (now.hour * 3600 + now.minute * 60 + now.second)

                if every:
                    t -= 86400

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

            if in_sent["day"] is None and in_sent["time"] is None:
                t -= now.hour * 3600 + now.minute * 60 + now.second

        elif w == "on":

            # if user writes on <day> skip this
            if in_sent["day"] is None:
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

    if every is True:
        every = t

    if t < 0:
        t = None

    return t, every


def whats_in_sent(true_sent):

    in_sent = {"time": None, "day": None, "on": False, "at": False}

    for word_ in true_sent:
        for time_ in times_dct:
            if word_ == time_:
                in_sent["time"] = word_

        for day_ in days_dct:
            if word_ == day_:
                in_sent["day"] = word_

        if word_ == "on":
            in_sent["on"] = True
        elif word_ == "at":
            in_sent["at"] = True
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
        ("weeks", 604800),
        ("days", 86400),
        ("h", 3600),
        ("min", 60),
        ("sec", 1),
    )

    result = []

    for name, count in intervals:
        value = seconds // count

        if value:
            seconds -= value * count

            if value == 1:
                name = name.rstrip("s")

            result.append("{} {}".format(value, name))

    return ", ".join(result)


# ex1 = ['tomorrow', 'tomorrow at 12', '1 day', '2 days at 22:00', 'fri', 'mon', 'sat at 9', '10 sec', '1 week', 'at 23:50',
#        'every day at 22', 'every 2 days at 14', 'every week at 7', 'every 10 h', 'every day']
#
# for e in ex1:
#     print('string:', e)
#     _ = sent_time_finder(e)[0]
#     print('date:', timestamp_to_local(_ + time.time()))
#     print('time to:', convert_sec(_))
#     print('-----------------------------')
