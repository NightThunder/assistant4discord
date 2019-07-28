from assistant4discord.discord_api.discord_client import run


if __name__ == "__main__":
    my_token = open("./token.txt", "r").read()
    run(method="w2v", model_name="model_v1.kv", my_token=my_token, log_chat=True)
