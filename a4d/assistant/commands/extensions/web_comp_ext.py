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
        min_time = 120        # min time between two website visits
        max_num_entries = 10  # max db entries for user
        max_num_links = 10    # max links allowed per entry

        if self.switch == 0:
            (self.time_to_message, self.every) = self.time_message()

            # block
            if (
                self.time_to_message >= min_time
                and await self.num_of_entries(str(self.message.author))
                < max_num_entries
            ):
                pass
            else:
                self.block = None
                raise ExtError("Min time is 120 sec. Max active site checks is 10.")

            self.links = list(set(self.get_links()))

            # block
            if len(self.links) > max_num_links:
                self.block = None
                raise ExtError("More then 10 links in message!")

            self.html_lst = await get_content(self.links, self.client)

            if None in self.html_lst:
                self.block = None
                raise ExtError("Invalid url!")

            self.switch += 1
        else:
            html_lst = await get_content(self.links, self.client)

            diff_str = ""
            no_diff_links = []

            for new_html, saved_html, link in zip(html_lst, self.html_lst, self.links):
                diff = self.get_diff(html2text(new_html), html2text(saved_html))
                if len(diff) != 0:
                    diff_str += "{}\n{}".format(link, diff)
                    diff_str += "\n" + 50 * "=" + "\n"
                else:
                    no_diff_links.append(link)

            diff_str = diff_str[:-52]
            self.html_lst = html_lst

            if len(diff_str) == 0 and len(no_diff_links) != 0:
                return "No difference in {}.".format(self.links)
            elif len(diff_str) != 0 and len(no_diff_links) == 0:
                return diff_str
            elif len(diff_str) != 0 and len(no_diff_links) != 0:
                return diff_str + "\n" + "No difference in {}.".format(no_diff_links)
            else:
                # this should never happen
                raise ExtError("Error: no difference and no links!")

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
            if l.startswith('?'):
                continue
            elif len(l) < 3:
                continue
            elif l.endswith("\n"):
                lines += l + "\n"
            else:
                pass

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
