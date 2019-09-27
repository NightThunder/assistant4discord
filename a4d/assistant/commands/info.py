from a4d.assistant.commands.helpers.master import Master


class AppInfo(Master):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***Info help***\n" 
            "Display basic information about this bot.\n"
            "Call: info```"
        )
        self.call = "info"

    async def get_app_info(self):
        app_info = await self.client.application_info()
        return app_info

    async def doit(self):
        app_info = await self.get_app_info()

        info_str = (
            "name: <@{}>\nowner: {}\ndescription: {}\npublic bot: {}\ngithub: https://github.com/NightThunder/assistant4discord"
            "\n-------------------------------\n"
            "type help for commands info".format(app_info.id, app_info.owner, app_info.description, app_info.bot_public))

        await self.send("{}".format(info_str))
