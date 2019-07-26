from .extensions.web_comp_class import WebComp
from .extensions.mongodb_helpers.tui import ShowItems, RemoveItem
from .extensions.mongodb_helpers.mongodb_adder import AddItem


class WebsiteComparison(AddItem):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***WebsiteComparison help***\n"
            "Looks for changes in a website.\n"
            "input: 1 >= websites\n"
            "Use: check <time when to check for changes>\n"
            "Note:\n"
            "- line unique to sequence 1\n"
            "+ line unique to sequence 2\n"
            "? line not present in either input sequence\n"
            "see: https://docs.python.org/3/library/difflib.html#difflib.Differ```"
        )
        self.call = "check stevilka"

        # bool, optional: set to True if helper object needs asyncio.sleep() .
        self.use_asyncio = True

    async def doit(self):
        await self.AddItem_doit(WebComp)


class ShowWebsites(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***ShowWebsites help***\n" "Show websites queued for checking.```"
        )
        self.call = "show websites"

    async def doit(self):
        await self.ShowItems_doit("WebsiteComparison")


class RemoveWebsite(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = "```***RemoveWebsite help***\n" "Remove website from queue.```"
        self.call = "remove website stevilka"

    async def doit(self):
        await self.RemoveItem_doit("WebsiteComparison")
