from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.notes_helper.note_class import Note
import os
import discord
from assistant4discord.assistant.commands.text_user_interface.tui import AddItem, ShowItems, RemoveItem


class NoteIt(AddItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***Note help***\n' \
                    'Make a note from previous message```'
        self.call = 'note'

    async def doit(self):
        await self.AddItem_doit(Note)


class ShowNotes(ShowItems):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***ShowNotes help***\n' \
                    'Display all user\'s notes```'
        self.call = 'show notes'

    async def doit(self):
        await self.ShowItems_doit('NoteIt')


class RemoveNote(RemoveItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***RemoveNote help***\n' \
                    'Remove user\'s note```'
        self.call = 'remove note stevilka'

    async def doit(self):
        await self.RemoveItem_doit('NoteIt')


class NotesTxt(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.help = '```***NotesTxt help***\n' \
                    'Sends user\'s notes in .txt```'
        self.call = 'notes to text'

    async def doit(self):

        all_notes = self.commands['NoteIt'].all_items
        user_notes = []

        for note in all_notes:
            if note.message.author == self.message.author:
                user_notes.append(str(note) + '\n--------------------\n')

        user_notes[-1] = user_notes[-1][:-23]

        if not user_notes:
            return

        file_name = '{}_notes.txt'.format(str(self.message.author)[:-4])
        with open(file_name, 'w') as file:
            file.write(''.join(user_notes))

        await self.message.channel.send(file=discord.File(file_name))

        os.remove(file_name)
