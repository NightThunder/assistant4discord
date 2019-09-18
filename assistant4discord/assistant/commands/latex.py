import os
import discord
from assistant4discord.assistant.commands.helpers.master import Master
from assistant4discord.assistant.commands.helpers.web_checker import get_content


class TextToLatex(Master):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***TextToLatex help***\n"
            "Convert latex text to png.\n"
            "Note: using https://www.codecogs.com/latex/eqneditor.php\n"
            "Call: latex```"
        )
        self.call = "latex"

    async def doit(self):
        """ Sends png of latex equation to discord.

        References
        ----------
        https://www.codecogs.com/latex/eqneditor.php
        https://jamesgregson.blogspot.com/2013/06/latex-formulas-as-images-using-python.html

        """
        file_name = 'latex_img.png'

        link = r'https://latex.codecogs.com/png.latex?\dpi{300}&space;\bg_white&space;%s' % self.message.content[6:]
        html = await get_content(link, self.client)

        with open(file_name, "wb") as f:
            f.write(html)

        await self.send(discord.File(file_name), is_file=True)

        os.remove(file_name)
