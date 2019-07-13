from assistant4discord.assistant.commands.website_comparison_helper.web_comp_class import WebComp
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class WebsiteComparison(AddItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***WebsiteComparison help***\n' \
                    'Looks for changes in a website.\n' \
                    'input: 1 >= websites\n' \
                    'Use: check <time when to check for changes>\n' \
                    '- line unique to sequence 1\n' \
                    '+ line unique to sequence 2\n' \
                    '? line not present in either input sequence\n' \
                    'see: https://docs.python.org/3/library/difflib.html#difflib.Differ```'
        self.call = 'check stevilka'
        self.use_asyncio = True

    async def doit(self):
        await self.AddItem_doit(WebComp)


class ShowWebsites(ShowItems):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***ShowWebsites help***\n' \
                    'Show websites queued for checking.```'
        self.call = 'show websites'

    async def doit(self):
        await self.ShowItems_doit('WebsiteComparison')


class RemoveWebsite(RemoveItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***RemoveWebsite help***\n' \
                    'Remove website from queue.```'
        self.call = 'remove website stevilka'

    async def doit(self):
        await self.RemoveItem_doit('WebsiteComparison')
