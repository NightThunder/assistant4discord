class Master:

    def __init__(self, client=None, db=None, message=None, commands=None, similarity=None):
        """ Base class for commands."""
        self.client = client
        self.db = db
        self.message = message
        self.commands = commands
        self.sim = similarity
        self.special = {}

    def check_rights(self):
        """ Verify that user owner or mod.

        Use in doit with special for command blocking.

        """
        mod_lst = self.commands["Mods"].all_items
        owner = mod_lst[0]

        if self.special.get("permission") == "owner" and self.message.author == owner:
            return True

        elif self.special.get("permission") == "mod" and self.message.author in mod_lst:
            return True

        else:
            return False
