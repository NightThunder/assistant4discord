class Master:

    def __init__(self, client=None, message=None, similarity=None):
        """ Base class for commands.

        Args:
            client: discord client object
            message: discord message object
            similarity: Similarity object from assistant4discord.nlp_tasks.similarity
        """
        self.client = client
        self.message = message
        self.sim = similarity
