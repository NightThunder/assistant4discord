from .extensions.web_comp_ext import WebComp
from .helpers.tui import ShowItems, RemoveItem
from .helpers.mongodb_adder import AddItem


class WebsiteComparison(AddItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***WebsiteComparison help***\n"
            "Looks for changes in a website.\n"
            "Call: check <time when to compare>\n"
            "Input: 1 >= websites\n"
            "Note:\n"
            "- line unique to sequence 1\n"
            "+ line unique to sequence 2\n"
            "? line not present in either input sequence\n"
            "see: https://docs.python.org/3/library/difflib.html#difflib.Differ\n"
            "Valid times: second, minute, hour, day, week, name of days, time in format at h:m:s dates in format on d/m/y.\n"
            "Warning: at and on MUST be used with times and dates.\n"
            "Warning: max 10 links per message, max 100 total websites, min time check is 120 sec```"
        )
        self.call = "check stevilka"
        self.special = {"response": "dm"}

    async def doit(self):
        await self.AddItem_doit(WebComp(client=self.client, message=self.message, db=self.db))


class ShowWebsites(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***ShowWebsites help***\n"
            "Show websites queued for checking.\n"
            "Call: show websites```"
        )
        self.call = "show websites"
        self.special = {"response": "dm"}

    async def doit(self):
        await self.ShowItems_doit(WebComp)


class RemoveWebsite(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveWebsite help***\n"
            "Remove website from your list.\n"
            "Call: remove website <number>```"
        )
        self.call = "remove website stevilka"
        self.special = {"response": "dm"}

    async def doit(self):
        await self.RemoveItem_doit(WebComp)
