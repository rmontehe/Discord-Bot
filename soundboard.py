import asyncio
import youtube_dl
import pafy
import os
import random
import discord
import time
from music import Player
from discord.ext import commands

class Soundboard(commands.Cog): # declare a class named player
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



    def setup(self):
        for guild in self.bot.guilds: # for each server that the bot is in, create an empty list variable to store songs for the queue
            self.voice_states[guild.id] = [] # creates a list containing the voice client for each server that the bot is in
