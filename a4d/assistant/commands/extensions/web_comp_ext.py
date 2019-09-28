from html2text import html2text
from difflib import Differ
from a4d.nlp_tasks.find_times import timestamp_to_local, convert_sec
from a4d.assistant.commands.helpers.web_checker import get_content
from a4d.assistant.commands.helpers.extend import Extend, ExtError


class WebComp(Extend):

    def __init__(self, **kwargs):
        """
        Other Parameters
        ----------------
        links: list of str
            List of links provided by user.
        html_lst: list of str
            Html of website.
        block: False or None
            If None then obj_error_check in mongodb_adder returns error.

        """
        super().__init__(**kwargs)
        self.name = "website_comparison"
        self.use_asyncio = True
        self.links = None
        self.html_lst = None
        self.block = False

    async def num_of_entries(self, author):
        cursor = self.db[self.name].find({"username": author})

        if cursor:
            return len(await cursor.to_list(length=None))
        else:
            return 0

    async def doit(self):

        diff_str = ""

        if self.switch == 0:
            (self.time_to_message, self.every) = self.time_message()

            # block
            if (
                self.time_to_message >= 120
                and await self.num_of_entries(str(self.message.author)) < 10
            ):
                pass
            else:
                self.block = None
                raise ExtError("Min time is 120 sec. Max active site checks is 10.")

            self.links = list(set(self.get_links()))

            # block
            if len(self.links) > 10:
                self.block = None
                raise ExtError("More then 10 links in message!")

            self.html_lst = await get_content(self.links, self.client)

            if None in self.html_lst:
                self.block = None
                raise ExtError("Invalid url!")

            self.switch += 1
        else:
            html_lst = await get_content(self.links, self.client)

            for new_html, saved_html, link in zip(html_lst, self.html_lst, self.links):
                diff = self.get_diff(html2text(new_html), html2text(saved_html))
                if len(diff) != 0:
                    diff_str += "{}\n{}".format(link, diff)
                    diff_str += "\n-----------------------------------\n"

            diff_str = diff_str[:-37]
            self.html_lst = html_lst

            if len(diff_str) == 0:
                return "Websites {} checked, no difference found.".format(self.links)
            else:
                return diff_str

    def get_links(self):
        """ Get links from discord message. """
        msg = self.get_message()
        return msg.split()

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

    def __str__(self):

        msg_str = ""
        for l in self.links:
            msg_str += l + "\n"

        if self.every:
            return "{}\ncheck set every {}\nnext check on {}".format(
                msg_str,
                convert_sec(self.every),
                timestamp_to_local(self.time_to_message + self.created_on),
            )
        else:
            return "{}\ncheck set for: {}".format(
                msg_str, timestamp_to_local(self.time_to_message + self.created_on)
            )
