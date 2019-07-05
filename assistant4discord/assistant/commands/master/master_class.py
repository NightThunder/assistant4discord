class Master:

    def __init__(self, client=None, message=None, commands=None, similarity=None, command_vectors=None, calls=None):
        """ Base class for commands."""
        self.client = client
        self.message = message
        self.commands = commands
        self.sim = similarity
        self.command_vectors = command_vectors
        self.calls = calls
