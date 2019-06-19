from assistant4discord.discord_api.discord_client import run


if __name__ == '__main__':
    my_token = open('./token.txt', 'r').read()
    run('model_v1.kv', my_token)
