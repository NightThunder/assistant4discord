class Master:

    def __init__(self, client=None, message=None, commands=None, special=None, similarity=None, calls=None):
        """ Base class for commands."""
        self.client = client
        self.message = message
        self.commands = commands
        self.special = special
        self.sim = similarity
        self.calls = calls

    def check_rights(self):
        mod_lst = self.commands['Mods'].all_items
        owner = mod_lst[0]

        if self.special.get('permission') == 'owner' and self.message.author == owner:
            return True

        elif self.special.get('permission') == 'mod' and self.message.author in mod_lst:
            return True

        else:
            return False
