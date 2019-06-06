from assistant4discord.assistant.commander import Ping
from assistant4discord.nlp_tasks.message_processing import process_message
from assistant4discord.nlp_tasks.wmd_similarity import get_similarity


listen_for = {'whats my ping': Ping}


def do_the_thing(message):

    sims = {}
    for text_command, command in listen_for.items():
        sims[command] = get_similarity(process_message(message), process_message(text_command))

    sims_k = list(sims.keys())
    sims_v = list(sims.values())

    print(sims_v)

    if max(sims_v) > 1:
        return sims_k[sims_v.index(max(sims_v))]
    else:
        return None


# TODO wmd not working well use addition
