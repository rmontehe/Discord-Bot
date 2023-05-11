import asyncio
import youtube_dl
import pafy
import os
import random
import discord
import time
from music import Player
from discord.ext import commands

class Soundboard(commands.Cog): # declare a class named soundboard
    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}

        self.setup()
        print("Initializing Soundboard...")


    async def play_sound(self, voice_client, sound): # ctx is the Context, song is the url link of the song that you want to play

        voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source = sound, pipe = True)))
        voice_client.source.volume = .15

    async def play_song(self, voice_client, music): # ctx is the Context, song is the url link of the song that you want to play

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


#########################################
####### Defining User Commands  #########
#########################################

    @commands.command()
    async def sb(self, ctx, sound): # define a command that allows users to indicate a sound that they would like played
                                    # granted that the indicated sound file is in the soundboard directory

        soundboardDir = os.listdir(f"./soundboard") # assign the directory to a variable

        if len(soundboardDir) == 0: # if there is no file in the user's directory
            print ("There are currently no sounds.") # print this message to the terminal for developer's purposes
            return await ctx.send("**There are currently no sounds.**") # send this message to the discord so users are aware

        else: # if there are soundfiles in the soundboard folder

            for file_name in soundboardDir:
                sound = sound.lower() # make sure that the input is all lowercase
                if sound in file_name: # if string is found in file file_name
                    sound = file_name # sound variable is now the respective mp3 file


            if ".mp3" not in sound: # if there was no match, then the sound variable should not have the string .mp3
                return await ctx.send("**No sound with this name.**")

            guildID = ctx.guild.id
            for voice_client in self.bot.voice_clients: # for each voice client instance of the bot
                if guildID is voice_client.guild.id: # if the guild id of the member matches the guild id of the voice client
                    voice = voice_client  # store this voice client as a variable

            soundpath = f"./soundboard/{sound}"

            if voice.is_playing() is True: # this produces an error, hopefully we can acess voice client objects of the player

                print("Beep Boop is playing music")
                voice.pause() # pause the music that is currently playing
                print("Music Paused")
                music = voice.source # save the source of the music as a variable

                sound = open(soundpath, "r")
                print("Sleeping music function to play soundboard-sound")
                play = asyncio.create_task(self.play_sound(voice, sound)) # in those 7 seconds allow the sound file to play
                await asyncio.sleep(7) # make the bot sleep for 7 seconds
                print("Sound Played")
                voice.stop() # stop the voice client so that you can start the music again, the music cannot start again if already playing something

                sound.close() # after the sound file is done playing, close the sound file

                await self.play_song(voice, music) # start playing the music again

            else:

                print("Beep Boop is not playing anything.")
                sound = open(soundpath, "r")
                await self.play_sound(voice, sound)
                sound.close()

    @commands.command()
    async def rand_sb(self, ctx):

        soundboardDir = os.listdir(f"./soundboard") # assign the directory to a variable

        randomIndex = random.randint(0, (len(soundboardDir) -1)) # generate a random index within the range of the length of the directory
        sound = soundboardDir[randomIndex]

        guildID = ctx.guild.id
        for voice_client in self.bot.voice_clients: # for each voice client instance of the bot
            if guildID is voice_client.guild.id: # if the guild id of the member matches the guild id of the voice client
                voice = voice_client  # store this voice client as a variable

        soundpath = f"./soundboard/{sound}"

        if voice.is_playing() is True: # this produces an error, hopefully we can acess voice client objects of the player

            print("Beep Boop is playing music")
            voice.pause() # pause the music that is currently playing
            print("Music Paused")
            music = voice.source # save the source of the music as a variable

            sound = open(soundpath, "r")
            print("Sleeping music function to play soundboard-sound")
            play = asyncio.create_task(self.play_sound(voice, sound)) # in those 7 seconds allow the sound file to play
            await asyncio.sleep(7) # make the bot sleep for 7 seconds
            print("Sound Played")
            voice.stop() # stop the voice client so that you can start the music again, the music cannot start again if already playing something

            sound.close() # after the sound file is done playing, close the sound file

            await self.play_song(voice, music) # start playing the music again

        else: # if the bot is not currently playing anything

            print("Beep Boop is not playing anything.")
            sound = open(soundpath, "r")
            await self.play_sound(voice, sound)
            sound.close()

    @commands.command()
    async def sounds(self, ctx): # define a command that displays the sounds in the soundbaord directory

        soundboardDir = os.listdir(f"./soundboard") # assign the directory to a variable

        embed = discord.Embed(title="Soundboard Sounds", description="", colour=discord.Colour.dark_gold()) # customize the discord embedded message

        for sound in soundboardDir:
            sound = sound.replace('.mp3','') # strings are immutable, cannot be changed
            embed.description += f"- {sound}\n"

        embed.set_footer(text="Use '!sb (sound)' to use the Soundboard.")
        await ctx.send(embed=embed)
