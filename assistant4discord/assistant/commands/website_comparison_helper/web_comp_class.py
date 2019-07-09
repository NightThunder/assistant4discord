from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.nlp_tasks.find_times import sent_time_finder, timestamp_to_utc
import aiohttp
import asyncio
import time
from html2text import html2text
from difflib import Differ
from aiohttp.client_exceptions import InvalidURL


class WebChecker(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        results = await asyncio.gather(*[self.client.loop.create_task(self.fetch(session, url)) for url in urls])
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = 0
        self.links = self.get_links()
        self.html_lst = None
        (self.time_to_message, self.every) = self.time_message()
        # first run in line 64 of tui.py

    async def to_do(self):

        html_lst = await self.get_content(self.links)

        if None in html_lst:
            return None

        diff_str = ''

        if self.n == 0:
            self.html_lst = html_lst
            self.n += 1
        else:
            for new_html, saved_html, link in zip(html_lst, self.html_lst, self.links):
                diff = self.get_diff(html2text(new_html), html2text(saved_html))
                if len(diff) != 0:
                    diff_str = '{}\n{}\n\n'.format(link, diff)

            self.html_lst = html_lst
            diff_str = diff_str[:-4]

        return diff_str

    @staticmethod
    def get_diff(s1, s2):
        s1 = s1.splitlines(keepends=True)
        s2 = s2.splitlines(keepends=True)

        d = Differ()

        result = list(d.compare(s1, s2))

        lines = ''
        for l in result:
            if l.startswith('  '):
                continue
            elif not l.endswith('\n'):
                lines += l + '\n'
            else:
                lines += l

        return lines

    def time_message(self):
        """ Parses message for time words.

        Returns: seconds to message
        """
        time_to_command, every = sent_time_finder(self.message.content[22:])

        return time_to_command, every

    def __str__(self):

        msg_str = ''
        for l in self.links:
            msg_str += l + '\n'

        if self.every:
            return '{}\ncheck set every: {}'.format(msg_str, timestamp_to_utc(int(self.time_to_message + time.time())))
        else:
            return '{}\nset for: {}'.format(msg_str, timestamp_to_utc(int(self.time_to_message + time.time())))
