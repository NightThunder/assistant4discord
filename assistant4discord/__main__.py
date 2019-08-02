from assistant4discord.discord_api.discord_client import run
import os


DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
MONGODB_TOKEN = os.environ['MONGODB_TOKEN']


if __name__ == "__main__":
    run(method="w2v", model_name="model_v1.kv", discord_token=DISCORD_TOKEN, mongodb_token=MONGODB_TOKEN, log_chat=True)
