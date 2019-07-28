import time
from html2text import html2text
from difflib import Differ
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc
from .helpers.web_checker import WebChecker


class WebComp(WebChecker):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        run_on_init: bool
            If True runs once on initialization.
        time_to_message: int
        every: bool
        n: int
            0 if never ran, 1 if ran once or more.
        links: list of str
            List of links provided by user.
        created_on: int
            When was this initialized.

        """
        super().__init__(**kwargs)
        self.name = 'website comparison'
        self.run_on_init = True
        self.use_asyncio = True
        self.time_to_message = None
        self.every = None
        self.n = 0
        self.links = None
        self.html_lst = None
        self.created_on = int(time.time())

    async def num_of_entries(self, author):
        cursor = self.db[self.name].find({'username': author})

        if cursor:
            return len(await cursor.to_list(length=None))
        else:
            return 0

    async def todo(self):

        diff_str = ""

        if self.n == 0:
            (self.time_to_message, self.every) = self.time_message()

            ######### blocking #########
            if self.every and self.time_to_message > 180 and await self.num_of_entries(str(self.message.author)) < 10:
                pass
            else:
                return None
            ############################

            self.links = list(set(self.get_links()))
            self.html_lst = await self.get_content(self.links)

            if None in self.html_lst:
                return None

            self.n += 1
        else:
            html_lst = await self.get_content(self.links)

            for new_html, saved_html, link in zip(html_lst, self.html_lst, self.links):
                diff = self.get_diff(html2text(new_html), html2text(saved_html))
                if len(diff) != 0:
                    diff_str += "{}\n{}".format(link, diff)
                    diff_str += "\n-----------------------------------\n"

            diff_str = diff_str[:-37]
            self.html_lst = html_lst

            print("checked websites!")

            self.created_on = int(time.time())
            return diff_str

    def get_links(self):

        c = 0
        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                links = msg.content.split()
                return links

        return None

    @staticmethod
    def get_diff(s1, s2):
        """ Get difference from two strings.

        Parameters
        ----------
        s1: str
        s2: str

        Returns
        -------
        str
            Diff string.

        References
        ----------
        https://docs.python.org/3/library/difflib.html#differ-example
        """

        s1 = s1.splitlines(keepends=True)
        s2 = s2.splitlines(keepends=True)

        d = Differ()

        result = list(d.compare(s1, s2))

        lines = ""
        for l in result:
            if l.startswith("  "):
                continue
            elif not l.endswith("\n"):
                lines += l + "\n"
            else:
                lines += l

        return lines

    def time_message(self):
        """ Parses message for time words.

        Returns
        -------
        int
            seconds to message
        """
        time_to_command, every = sent_time_finder(self.message.content)

        return time_to_command, every

    def __str__(self):

        msg_str = ""
        for l in self.links:
            msg_str += l + "\n"

        if self.every:
            return "{}\ncheck set every: {}".format(
                msg_str, timestamp_to_utc(self.time_to_message + self.created_on)
            )
        else:
            return "{}\nset for: {}".format(
                msg_str, timestamp_to_utc(self.time_to_message + self.created_on)
            )
