from assistant4discord.discord_api.discord_client import run


if __name__ == '__main__':
    my_token = open('./token.txt', 'r').read()
    run(method='w2v', model_name='model_v1.kv', my_token=my_token, log_chat=True)

# print(self.client.guilds)
# print(self.client.users)
# print(self.client.private_channels)
# info = await self.client.application_info()
# print(info.owner)

# TODO: admin commands, add admins
