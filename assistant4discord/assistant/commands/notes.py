from assistant4discord.assistant.commands.master.master_class import Master
from assistant4discord.assistant.commands.notes_helper.note_class import Note
from assistant4discord.nlp_tasks.message_processing import word2vec_input
import os
import discord


class NoteIt(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'note'
        self.help = '```***Note help***\n' \
                    'Make a note from previous message```'
        self.all_notes = []

    async def doit(self):
        note = Note(client=self.client, message=self.message)

        if note:
            self.all_notes.append(note)
            await self.message.channel.send('Noted!')
        else:
            await self.message.channel.send('something went wrong')


class ShowNotes(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'show notes'
        self.help = '```***ShowNotes help***\n' \
                    'Display all user\'s notes```'

    async def doit(self, get_note_str=False):

        all_notes = self.commands['NoteIt'].all_notes
        note_str = ''
        n_notes = 0
        for i, note in enumerate(all_notes):
            if note.message.author == self.message.author:
                note_str += '**note {}:** {}\n'.format(i, str(note))

                if i != len(all_notes) - 1:
                    note_str += '--------------------\n'

                n_notes += 1

        if n_notes != 0:
            if get_note_str:
                return note_str
            else:
                await self.message.channel.send(note_str)
        else:
            await self.message.channel.send('You have no notes!')


class RemoveNote(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'remove note'
        self.help = '```***RemoveNote help***\n' \
                    'Remove user\'s note```'

    async def doit(self):

        try:
            to_remove = int(word2vec_input(self.message.content[22:], replace_num=False)[-1])
        except ValueError:
            await self.message.channel.send('something went wrong')
            return

        all_notes = self.commands['NoteIt'].all_notes
        n_notes = 0
        for i, note in enumerate(all_notes):
            if note.message.author == self.message.author and i == to_remove:
                all_notes.pop(i)
                break
            else:
                n_notes += 1

        if to_remove > n_notes:
            await self.message.channel.send('Could not find that note!')
        else:
            await self.message.channel.send('Note {} removed!'.format(to_remove))


class NotesTxt(Master):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = 'notes to text'
        self.help = '```***NotesTxt help***\n' \
                    'Sends user\'s notes in .txt```'

    async def doit(self):
        self.commands['ShowNotes'].message = self.message
        user_notes = await self.commands['ShowNotes'].doit(get_note_str=True)

        if not user_notes:
            return

        file_name = '{}_notes.txt'.format(str(self.message.author)[:-4])
        with open(file_name, 'w') as file:
            file.write(user_notes)

        await self.message.channel.send(file=discord.File(file_name))

        os.remove(file_name)
