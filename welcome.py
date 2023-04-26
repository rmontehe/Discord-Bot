import asyncio
import youtube_dl
import pafy
import os
import random
import discord
import time
from music import Player
from discord.ext import commands


class Intercom(commands.Cog): # declare a class named player
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

        self.setup()
        print("Initializing Intercom...")


        @self.bot.event
        async def on_voice_state_update(member, before, after): # register the event when a A MEMBER'S VOICE STATE CHANGES

            if member.bot is True: # if the member who's voice status was updated IS A BOT

                for guild_id in self.voice_states: # for each guild the bot is in iterate through the voice_states list
                    if guild_id is member.guild.id: # if the guild id matches the guild id of the member

                        print("This is the guild id: " + str(guild_id))
                        self.voice_states[guild_id] = member.voice # assign the voice_client of that server the new voice_status, we now have the information of the voice
                        print(self.voice_states[guild_id])
                        print("This is the before state: " + str(before.channel))
                        print("This is the after state: " + str(after.channel))

                        print(os.listdir("./welcome"))

            if member.bot is False: # if the member that changed voice state is a user and not a bot

                guildID = member.guild.id # assign a variable for the ID of the guild
                if self.voice_states[guildID].channel is not None and after.channel is not None and after.channel is self.voice_states[guildID].channel and before.channel is not self.voice_states[guildID].channel: # if the bot in this guild IS IN a voice channel, if a member JOINED a voice channel, AND the voice channel is the SAME as the bot

                    print(f"{member.name} joined {after.channel.name}") # allows for coder to retrieve information on who regularly joins the server calls, provides the Username and ID
                    print(f"{member.name}'s ID is {member.id}") # this information is important for accessing a directory (named after their ID) containing sound files

                    userID = str(member.id)
                    print("These are the bot Voice Clients: " + str(bot.voice_clients))

                    for voice_client in bot.voice_clients: # for each voice client instance of the bot

                        if guildID is voice_client.guild.id: # if the guild id of the member matches the guild id of the voice client
                            voice = voice_client  # store this voice client as a variable

                    if userID in os.listdir("./welcome"): # if the user has a folder in the directory

                        welcomeDir = os.listdir(f"./welcome/{userID}") # assign the directory to a variable

                        if len(welcomeDir) == 0: # if there is no file in the user's directory
                            print (f"{member.name} does not currently have a welcome sound.") # print this message to the command prompt

                        else: # if there is only one file in the user's directory

                            randomIndex = random.randint(0, (len(welcomeDir) -1)) # generate a random index within the range of the length of the directory
                            name = welcomeDir[randomIndex]

                            soundPath = f"./welcome/{userID}/{name}"

                            if voice.is_playing() is True: # this produces an error, hopefully we can acess voice client objects of the player

                                print("Beep Boop is playing music")
                                voice.pause() # pause the music that is currently playing
                                print("Music Paused")
                                music = voice.source # save the source of the music as a variable

                                sound = open(f"./welcome/{userID}/{name}", "r")
                                print("Sleeping music function to play welcome-sound")
                                play = asyncio.create_task(self.play_sound(voice, sound)) # in those 7 seconds allow the sound file to play
                                await asyncio.sleep(7) # make the bot sleep for 7 seconds
                                print("Sound Played")
                                voice.stop() # stop the voice client so that you can start the music again, the music cannot start again if already playing something

                                sound.close() # after the sound file is done playing, close the sound file

                                await self.play_song(voice, music) # start playing the music again

                            else:

                                print("Beep Boop is not playing anything.")
                                sound = open(f"./welcome/{userID}/{name}", "r")
                                await self.play_sound(voice, sound)
                                sound.close()

                if self.voice_states[guildID].channel is not None and before.channel is not None and before.channel is self.voice_states[guildID].channel and after.channel is None:

                    print(f"{member.name} left the {before.channel.name}")# allows for coder to retrieve information on who regularly joins the server calls, provides the Username and ID
                    print(f"{member.name}'s ID is {member.id}") # this information is important for accessing a directory (named after their ID) containing sound files





    @commands.command()
    async def test(self, ctx):
        user = ctx.author

        if user.voice is None: # if the user is not connected to a voice channel
            return await ctx.send("**Please connect to a voice Channel to interact with Beep Boop.**")

        if ctx.voice_client is not None and user.voice.channel != ctx.voice_client.channel: # if the bot is in a channel AND the user is not in the same channel
            return await ctx.send("**Beep Boop is not in your current Voice Channel.**")

        poll = discord.Embed(title=f"Beep Boop Soundboard Sounds", description="**Use '!sb {sound}' to play the sound you want.**", colour=discord.Colour.blue())
        poll.add_field(name="Previous", value = ":arrow_left:")
        poll.add_field(name = "Next", value = ":arrow_right")
#        poll.set_footer(text="Voting ends in 15 seconds.")

        poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions,
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2190") # left arrow
        await poll_msg.add_reaction(u"\u2192") # right arrow

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

    async def play_sound(self, voice_client, sound): # ctx is the Context, song is the url link of the song that you want to play

        # bot voice_client will play the song from the url using the FFMpegPCM Audio and PCMVolumeTransformer.
        # FFMpeg is an audio format that is easy for discord to use
        # I would personally prefer to use these functions because it allows me to alter the bot's audio from within the code
        # after the song is finished playing, the bot will then check song queue. if there is a songe, it will play the song
        voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source = sound, pipe = True)))
        voice_client.source.volume = .15

    async def play_song(self, voice_client, music): # ctx is the Context, song is the url link of the song that you want to play

        # bot voice_client will play the song from the url using the FFMpegPCM Audio and PCMVolumeTransformer.
        # FFMpeg is an audio format that is easy for discord to use
        # I would personally prefer to use these functions because it allows me to alter the bot's audio from within the code
        # after the song is finished playing, the bot will then check song queue. if there is a songe, it will play the song
        if type(music) is not str:
            voice_client.play((music), after=lambda error: self.bot.loop.create_task(self.check_queue(voice_client)))

        if type(music) is str:
            music = pafy.new(music)
            url = music.getbestaudio().url
            voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(voice_client)))

        voice_client.source.volume = .05

    async def check_queue(self, voice_client):

        song_queue_name = self.bot.cogs["Player"].song_queue_name
        song_queue_url = self.bot.cogs["Player"].song_queue_url
        guildID = voice_client.guild.id

        if len(song_queue_url[guildID]) > 0: # if the length of the song queue is > 0, in other words if there is a song in queue for this particular server
            await self.play_song(voice_client, song_queue_url[guildID][0]) # play the first song in the queue list for this particular server
            song_queue_url[guildID].pop(0) # remove the first song from the queue list
            song_queue_name[guildID].pop(0) # remove the first song from the queue list

        else:
            return



    def setup(self):
        for guild in self.bot.guilds: # for each server that the bot is in, create an empty list variable to store songs for the queue
            self.voice_states[guild.id] = [] # creates a list containing the voice client for each server that the bot is in


    #NEED TO UPDATE self.voice_states() when the status of the bot changes (for each server)
        # INCLUDES CONNECT, DISCONNECT, CHANGE OF CHANNEL


        # if self.bot.voice_states.id is
        # if before is None or before.channel is not : # if the user was not in a voice channel,
        # return
