class Master:

    def __init__(self, client=None, message=None, similarity=None, commands=None, command_vectors=None, calls=None):
        """ Base class for commands."""
        self.client = client
        self.message = message
        self.sim = similarity
        self.commands = commands
        self.command_vectors = command_vectors
        self.calls = calls
