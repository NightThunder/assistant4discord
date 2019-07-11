# assistant4discord
This is a discord bot that uses discord API with discord.py rewrite. It is meant to be run privatly on a PC or on a respberry pi.

**What does it do:**
- dynamically import custom commands
- use word2vec to recognize user input
- use cosine similarity on sentences presented by word2vec to chose the best command

**Commands:**
- look for changes in a website
- play with word2vec model
- run any command at a given time
- remind me
- make a note
- help command

**Model**  
Built with reddit comments. Comments were collected from r/askreddit, r/gaming, r/math and r/physics. Model was trained with Gensim using window size 3, min count 20, 10 epochs and 300d vectors. There are approximately 50k different words in this model.

**Other functionalities**  
Text user interface for building discord chat menus. Find times in sentence (not using word2vec).

**How to use**  
My model can be downloaded from [here](https://github.com/NightThunder/assistant4discord/releases/download/v1.0.0-beta/model_v1.tar.gz). Extract it and move it to assistant4discord/data/models/. Discord token can be obtained from [here](https://discordapp.com/developers/applications/). Make a token.txt file, paste token inside and put it in the same directory as _/_main_/_. Run _/_main_/_.

