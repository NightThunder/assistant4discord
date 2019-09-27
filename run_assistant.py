from a4d.discord_api.discord_client import run
import os


DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
MONGODB_TOKEN = os.environ['MONGODB_TOKEN']


run(method="tf", discord_token=DISCORD_TOKEN, mongodb_token=MONGODB_TOKEN, log_chat=False)
# run(method="w2v", model_name="model_v1.kv", discord_token=DISCORD_TOKEN, mongodb_token=MONGODB_TOKEN, log_chat=False)
