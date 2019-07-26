import os
import discord
from .master.master_class import Master
from .extensions.note_class import Note
from .extensions.mongodb_helpers.tui import ShowItems, RemoveItem
from .extensions.mongodb_helpers.mongodb_adder import AddItem


class NoteIt(AddItem):

    def __init__(self):
        super().__init__()
        self.help = "```***Note help***\n" "Make a note from previous message```"
        self.call = "note"

    async def doit(self):
        await self.AddItem_doit(Note)


class ShowNotes(ShowItems):

    def __init__(self):
        super().__init__()
        self.help = "```***ShowNotes help***\n" "Display all user's notes```"
        self.call = "show notes"

    async def doit(self):
        await self.ShowItems_doit("NoteIt")


class RemoveNote(RemoveItem):

    def __init__(self):
        super().__init__()
        self.help = "```***RemoveNote help***\n" "Remove user's note```"
        self.call = "remove note stevilka"

    async def doit(self):
        await self.RemoveItem_doit("NoteIt")


class NotesTxt(Master):

    def __init__(self):
        super().__init__()
        self.help = "```***NotesTxt help***\n" "Sends user's notes in .txt```"
        self.call = "notes to text"

    async def doit(self):

        all_notes = self.commands["NoteIt"].all_items
        user_notes = []

        for note in all_notes:
            if note.message.author == self.message.author:
                user_notes.append(str(note) + "\n--------------------\n")

        user_notes[-1] = user_notes[-1][:-22]

        if not user_notes:
            return

        file_name = "{}_notes.txt".format(str(self.message.author)[:-4])
        with open(file_name, "w") as file:
            file.write("".join(user_notes))

        await self.message.channel.send(file=discord.File(file_name))

        os.remove(file_name)
