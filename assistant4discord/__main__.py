from assistant4discord.discord_api.discord_client import run


if __name__ == '__main__':
    my_token = open('./token.txt', 'r').read()
    run('model_v1.kv', my_token)


# TODO https://aiohttp.readthedocs.io/en/stable/client_reference.html
# TODO https://stackoverflow.com/questions/35879769/fetching-multiple-urls-with-aiohttp-in-python-3-5
