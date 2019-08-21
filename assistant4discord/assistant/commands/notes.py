import os
import discord
from assistant4discord.assistant.commands.helpers.master import Master
from .extensions.note_class import Note
from .helpers.tui import ShowItems, RemoveItem
from .helpers.mongodb_adder import AddItem


class NoteIt(AddItem):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***Note help***\n" "Make a note from previous message\n" "Call: note```"
        )
        self.call = "note"

    async def doit(self):
        await self.AddItem_doit(Note)


class ShowNotes(ShowItems):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***ShowNotes help***\n"
            "Display all user's notes\n"
            "Call: show notes```"
        )
        self.call = "show notes"

    async def doit(self):
        await self.ShowItems_doit(Note)


class RemoveNote(RemoveItem):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***RemoveNote help***\n"
            "Remove user's note\n"
            "Call remove note <number>```"
        )
        self.call = "remove note stevilka"

    async def doit(self):
        await self.RemoveItem_doit(Note)


class NotesTxt(Master):
    def __init__(self):
        super().__init__()
        self.help = (
            "```***NotesTxt help***\n"
            "Sends user's notes in .txt"
            "Call: notes to text```"
        )
        self.call = "notes to text"

    async def get_user_docs(self, author):
        cursor = self.db["note_it"].find({"username": author})
        return await cursor.to_list(length=None)

    async def doit(self):

        user_notes = await self.get_user_docs(str(self.message.author))

        notes_file = ""
        for note in user_notes:
            notes_file += note["text"] + "\n-----------------------------------\n"

        notes_file = notes_file[:-37]

        if not notes_file:
            await self.send("no notes")
            return

        file_name = "{}_notes.txt".format(str(self.message.author)[:-4])
        with open(file_name, "w") as file:
            file.write(notes_file)

        await self.send(discord.File(file_name), is_file=True)

        os.remove(file_name)
