import asyncio
import youtube_dl
import pafy
import discord
from discord.ext import commands

class Intercom(commands.Cog): # declare a class named player
    def __init__(self,bot):
        self.bot = bot
        self.voice_clients = {}

        self.setup()
        print("Initializing Intercom...")

        @self.bot.event
        async def on_voice_state_update(member, before, after): # register the event when a A MEMBER'S VOICE STATE CHANGES

            if member.bot is True: # if the member who's voice status was updated IS A BOT

                for guild_id in self.voice_clients: # for each guild the bot is in iterate through the voice_clients list
                    if guild_id is member.guild.id: # if the guild id matches the guild id of the member

                        print("This is the guild id: " + str(guild_id))
                        self.voice_clients[guild_id] = member.voice # assign the voice_client of that server the new voice_status, we now have the information of the voice
                        print(self.voice_clients[guild_id])
                        print("This is the before state: " + str(before.channel))
                        print("This is the after state: " + str(after.channel))

            if member.bot is False: # if the member that changed voice state is a user and not a bot

                guildID = member.guild.id # assign a variable for the ID of the guild
                if self.voice_clients[guildID].channel is not None and after.channel is not None and after.channel is self.voice_clients[guildID].channel: # if the bot in this guild IS IN a voice channel, if a member JOINED a voice channel, AND the voice channel is the SAME as the bot

                    print(f"{member.name} joined {after.channel.name}") # allows for coder to retrieve information on who regularly joins the server calls, provides the Username and ID
                    print(f"{member.name}'s ID is {member.id}") # this information is important for accessing a directory (named after their ID) containing sound files

                if self.voice_clients[guildID].channel is not None and before.channel is not None and before.channel is self.voice_clients[guildID].channel and after.channel is None:

                    print(f"{member.name} left the {before.channel.name}")# allows for coder to retrieve information on who regularly joins the server calls, provides the Username and ID
                    print(f"{member.name}'s ID is {member.id}") # this information is important for accessing a directory (named after their ID) containing sound files








    def setup(self):
        for guild in self.bot.guilds: # for each server that the bot is in, create an empty list variable to store songs for the queue
            self.voice_clients[guild.id] = [] # creates a list containing the voice client for each server that the bot is in


    #NEED TO UPDATE self.voice_clients() when the status of the bot changes (for each server)
        # INCLUDES CONNECT, DISCONNECT, CHANGE OF CHANNEL


        # if self.bot.voice_clients.id is
        # if before is None or before.channel is not : # if the user was not in a voice channel,
        # return
