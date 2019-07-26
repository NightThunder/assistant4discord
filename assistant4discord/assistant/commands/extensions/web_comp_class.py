import aiohttp
import asyncio
import time
from html2text import html2text
from difflib import Differ
from aiohttp.client_exceptions import InvalidURL
from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc


class WebChecker(Master):
    """ Get content of a website.

    Note
    ----
    Works with list of websites. Websites in message must be split with any whitespace.

    References
    ----------
    https://aiohttp.readthedocs.io/en/stable/client_reference.html
    https://stackoverflow.com/questions/35879769/fetching-multiple-urls-with-aiohttp-in-python-3-5
    https://faust.readthedocs.io/en/latest/_modules/aiohttp/client.html
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    async def fetch(session, url):

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()

                return await response.text()

        except InvalidURL:
            return None

    async def fetch_all(self, session, urls):
        results = await asyncio.gather(
            *[self.client.loop.create_task(self.fetch(session, url)) for url in urls]
        )
        return results

    async def get_content(self, urls):

        async with aiohttp.ClientSession() as session:
            htmls = await self.fetch_all(session, urls)
            return htmls

    def get_links(self):

        c = 0
        for msg in reversed(self.client.cached_messages):
            if msg.author == self.message.author:
                c += 1

            if c == 2:
                links = msg.content.split()
                return links

        return None


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
        (self.time_to_message, self.every) = self.time_message()
        self.n = 0
        self.links = self.get_links()
        self.html_lst = None
        self.created_on = time.time()

    async def to_do(self):

        html_lst = await self.get_content(self.links)

        if None in html_lst:
            return None

        diff_str = ""

        if self.n == 0:
            self.html_lst = html_lst
            self.n += 1
        else:
            for new_html, saved_html, link in zip(html_lst, self.html_lst, self.links):
                diff = self.get_diff(html2text(new_html), html2text(saved_html))
                if len(diff) != 0:
                    diff_str = "{}\n{}\n\n".format(link, diff)

            self.html_lst = html_lst
            diff_str = diff_str[:-4]

        print("checked websites!")
        return diff_str

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
                msg_str, timestamp_to_utc(int(self.time_to_message + self.created_on))
            )
        else:
            return "{}\nset for: {}".format(
                msg_str, timestamp_to_utc(int(self.time_to_message + self.created_on))
            )
