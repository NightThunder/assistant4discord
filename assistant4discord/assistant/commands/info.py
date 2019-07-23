from assistant4discord.assistant.commands.master.master_class import Master


class AppInfo(Master):

    def __init__(self):
        super().__init__()
        self.help = (
            "```***Info help***\n" "Display basic information about this bot.```"
        )
        self.call = "info"

    async def get_app_info(self):
        app_info = await self.client.application_info()
        return app_info

    async def doit(self):
        app_info = await self.get_app_info()

        info_str = (
            "name: <@{}>\nowner: {}\ndescription: {}\npublic bot: {}\n-------------------------------\ntype "
            "help for command info".format(app_info.id, app_info.owner, app_info.description, app_info.bot_public))

        await self.message.channel.send("{}".format(info_str))
