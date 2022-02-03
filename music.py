import asyncio
import youtube_dl
import pafy
import discord
from discord.ext import commands

class Player(commands.Cog): # declare a class named player
    def __init__(self, bot): # define initialization method
        self.bot = bot       # assign attribute of initialization as the input bot variables
        self.song_queue_url = {} # initialize song_queue_url varaible as an empty dictionary
        self.song_queue_name = {} # initialize song_queue_name varaible as an empty dictionary

        self.setup()
        print("Initializing Player...")

    def setup(self):
        for guild in self.bot.guilds: # for each server that the bot is in, create an empty list variable to store songs for the queue
            self.song_queue_url[guild.id] = [] # creates a song_url queue list for each server that the bot is in
            self.song_queue_name[guild.id] = [] # creates a song_name queue list for each server that the bot is in


    async def check_queue(self,ctx):
        if len(self.song_queue_url[ctx.guild.id]) > 0: # if the length of the song queue is > 0, in other words if there is a song in queue for this particular server
            await self.play_song(ctx, self.song_queue_url[ctx.guild.id][0]) # play the first song in the queue list for this particular server
            self.song_queue_url[ctx.guild.id].pop(0) # remove the first song from the queue list
            self.song_queue_name[ctx.guild.id].pop(0) # remove the first song from the queue list


    async def search_song(self, amount, song, get_url=False): # amount = amount of songs we want, the song you want to look up, whether you want to get the url

        # we don't want the bot to wait, so we use loop.run_in_executor() because we don't want to block the bot function and have the bot wait
        # we use .YoutubeDL() to search to pass specific parameters like "bestaudio" format, and "quiet" = true, for our YoutubeDL search
        # we use .extract_info() to extract the information we gathered from our search
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key = "YoutubeSearch"))

        if len(info["entries"]) == 0:
            return None

        # return the webpage_url for each entry in the info list if get_url == True, return the info list if get_url == False
        return [entry for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song): # ctx is the Context, song is the url link of the song that you want to play
        song = pafy.new(song)
        url = song.getbestaudio().url

        # bot voice_client will play the song from the url using the FFMpegPCM Audio and PCMVolumeTransformer.
        # FFMpeg is an audio format that is easy for discord to use
        # I would personally prefer to use these functions because it allows me to alter the bot's audio from within the code
        # after the song is finished playing, the bot will then check song queue. if there is a songe, it will play the song
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        await ctx.send(f"**Now playing: __{song.title}__**")
        ctx.voice_client.source.volume = .05


    @commands.command()
    async def join(self, ctx):
        user = ctx.author # given the context we ID who the user is

        # check if user is in a voice channel
        if user.voice is None: # if the user is not in a voice channel
            return await ctx.send("**You are not connected to a Voice Channel. Please join a Voice Channel to interact with Beep Boop.**")

        voiceChannel = user.voice.channel # ID which voice channel the user is in

        # check if bot is already in a voice channel that is not the channel the user is in
        if ctx.voice_client is not None and ctx.voice_client is not voiceChannel: # if the bot is in a voice channel, and is not in the same voice channel as the user
            await ctx.voice_client.disconnect() # disconnect the bot from the channel it is currently in

        # check if bot is in the voice channel
        if ctx.voice_client is voiceChannel: # if the bot is in the voice channel already
            return await ctx.send("**Beep Boop is already connected.**")
        await voiceChannel.connect(timeout=300) # connect to the voice channel that the user is in


    @commands.command()
    async def play(self, ctx, *, song=None):
        user = ctx.author
        voiceChannel = user.voice.channel

        if user.voice == None: # if the user is not in a voice channel
            await ctx.send("**Please join a Voice Channel to interact with Beep Boop.**")

        if song is None: # if no song or url is provided
            return await ctx.send("**You must provide a song to play.**")

        if ctx.voice_client is None: # if bot is not in a Voice Channel
            await voiceChannel.connect() # bot joins the voice channel that the user is in

        if ctx.voice_client is not None and ctx.voice_client.channel is not voiceChannel: # if the bot is in a voice channel that the user is not in
            await ctx.voice_client.disconnect() # disconnect from the current channel
            await voiceChannel.connect() # connect to the voice channel that the user is currently in

        # when the input song is not a youtube url
        if not ("youtube.com/watch?" in song or "http://youtu.be/" in song): # if the song is not a youtube link
            await ctx.send("**Searching for song, this may take a few seconds.**")

            # use the search function to get url
            results = await self.search_song(1, song, get_url=True)

            if results is None: # if no search results appeared
                return await ctx.send("**Sorry, I could not find the song you are looking for. Try using my 'search' command.**")

            song_url = results[0]["webpage_url"] # assign a variable the url string value
            song_name = results[0]["title"] # assign a variable the video title string value

        if ("youtube.com/watch?" in song or "http://youtu.be/" in song):
            song_url = song
            results = await self.search_song(1, song, get_url=True)
            song_name = results[0]["title"]

        if ctx.voice_client.source is not None and ctx.voice_client.is_playing(): # if there is something playing
            queue_len = len(self.song_queue_url[ctx.guild.id]) # retrieves the length of the song queue for the server

            if queue_len < 30 : # if the length of the current queue is less than 30
                self.song_queue_url[ctx.guild.id].append(song_url) # add this song url to the end of the queue list of this server
                self.song_queue_name[ctx.guild.id].append(song_name) # add this song name to the end of the queue list of this server
                return await ctx.send(f"**Song currently playing, __{song_name}__ has been added to the queue at position: {queue_len+1}.**")

            else: # if the length of the queue is greater than 30 songs
                return await ctx.send("**I can only queue up to 30 songs at a time, please wait for the current song to finish.**")

        await self.play_song(ctx, song_url) # play song through bot using PCM volume Transformer to allow for volume to be modified


    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None: # if the user did not indicate a song
            return await ctx.send("**Please indicate a song to search for.**")

        await ctx.send("**Searching for song, this may take a few seconds.**")
        info = await self.search_song(5, song) # search and get info for 5 songs
        embed = discord.Embed(title=f"Results for '{song}':", description="*You can use these URL's to play an exact song if the one you wanted is not the first result.*\n", colour=discord.Colour.red()) # create a discord embed post

        amount = 0
        for entry in info["entries"]: # for each song entry
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n" # add to the embed description
            amount += 1 # increment the amount variable

        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed = embed) # bot sends a message to channel with the embed of the searched songs

    @commands.command()
    async def queue(self, ctx): # display the current server/guild's queue
        if len(self.song_queue_name[ctx.guild.id]) == 0:
            return await ctx.send("**There are currently no songs in the queue.**")
        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for name in self.song_queue_name[ctx.guild.id]:
            embed.description += f"({i}) {name}\n"
            i += 1
        embed.set_footer(text="Thanks for using me!")
        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        user = ctx.author

        if user.voice is None: # if the user is not connected to a voice channel
            return await ctx.send("**Please connect to a voice Channel to interact with Beep Boop.**")

        if ctx.voice_client is not None and user.voice.channel != ctx.voice_client.channel: # if the bot is in a channel AND the user is not in the same channel
            return await ctx.send("**Beep Boop is not in your current Voice Channel.**")

        if ctx.voice_client is not None and ctx.voice_client.is_playing() is not True: # if bot is in a voice channel AND bot is not playing something AND the user is in the same channel
            return await ctx.send("**A song is not playing currently.**")

        poll = discord.Embed(title=f"Vote to Skip Song by - {ctx.author.name}#{ctx.author.discriminator}", description="**50% of the voice channel must vote to skip for it to pass.**", colour=discord.Colour.blue())
        poll.add_field(name="Skip", value = ":white_check_mark:")
        poll.add_field(name = "Stay", value = ":no_entry_sign:")
        poll.set_footer(text="Voting ends in 15 seconds.")

        poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions,
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705") # yes
        await poll_msg.add_reaction(u"\U0001F6AB") # no

        await asyncio.sleep(15) # 15 seconds to Vote

        poll_msg = await ctx.channel.fetch_message(poll_id)

        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]: # if the emoji is one of the yes or no emojis
                async for user in reaction.users(): # loop through each user that has reacted
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot: # (1) user is in same voice channel as bot, (2) user is not in reacted, (3) user is not a bot
                        votes[reaction.emoji] += 1

                        reacted.append(user.id)

        skip = False

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\U0001F6AB"] + votes[u"\u2705"]) > 0.49: # if no one voted no, or if the percentage of people who want to skip is > 50%
                skip = True # reset the value of skip to true
                embed = discord.Embed(title="Skip Successful", description="***Voting to skip the current song was successful, skipping now.***", colour= discord.Colour.dark_gold())


        if not skip: # if skip is not true, if at the end we should not skip
            embed = discord.Embed(title="Skip Unsuccessful", description="***Voting to skip the current song has failed.\n\n Voting failed, the vote requires at least 50% of the members to skip.***", colour= discord.Colour.red())

        embed.set_footer(text="Voting has ended.")

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed=embed)

        if skip:
            ctx.voice_client.stop()

    @commands.command()
    async def leave(self, ctx):
        user = ctx.author # given the context we ID who the user is
        if user.voice == None: # if the user is not in a voice channel
            await ctx.send("**Please join a Voice Channel to interact with Beep Boop.**")

        else: # if the user is in a voice channel
            voice = ctx.voice_client.channel

            if voice is None: # if the bot is not in a channel
                await ctx.send("**Beep Boop is not connected to a channel.**")

            elif voice is not user.voice.channel: # if the bot is in a channel, but not the same channel as the user
                await ctx.send("**Please be in the same Voice Channel as Beep Boop.**")

            else: # if the bot is in a channel
                await ctx.voice_client.disconnect() # disconnect from the current voice channel

    @commands.command()
    async def pause(self, ctx):
        user = ctx.author # given the context we ID who the user is
        if user.voice.channel == None: # if the user is not in a voice channel
            await ctx.send("**Please join a Voice Channel to interact with Beep Boop.**")
        else: # if the user is in a voice Channel
            voice = ctx.voice_client
            if voice.is_playing():
                voice.pause()
            else:
                await ctx.send("**Beep Boop is not playing anything.**")

    @commands.command()
    async def resume(self, ctx):
        user = ctx.author # given the context we ID who the user is
        if user.voice == None: # if the user is not in a voice channel
            await ctx.send("**Please join a Voice Channel to interact with Beep Boop.**")
        else: # if the user is in a voice Channel
            voice = ctx.voice_client
            if voice.is_paused():
                voice.resume()
            else:
                await ctx.send("**Beep Boop is not paused.**")

    @commands.command()
    async def stop(self, ctx):
        user = ctx.author # given the context we ID who the user is
        if user.voice == None: # if the user is not in a voice channel
            await ctx.send("**Please join a Voice Channel to interact with Beep Boop.**")
        else: # if the user is in a voice Channel
            ctx.voice_client.stop()
