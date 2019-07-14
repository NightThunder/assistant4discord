class Master:

    def __init__(self, client=None, message=None, commands=None, similarity=None, calls=None):
        """ Base class for commands."""
        self.client = client
        self.message = message
        self.commands = commands
        self.sim = similarity
        self.calls = calls
