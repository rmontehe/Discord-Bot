# import relevant python libraries
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv # python library that allows you to load variables from a .env file
from music import Player
from api import API_Vendor
from welcome import Intercom

load_dotenv() # loads the .env variables to the

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)  # create an instance of a client, the connection to Discord

#########################################
########## Defining Functions ###########
#########################################

async def setup():
    await client.wait_until_ready()
    client.add_cog(Player(client))
    client.add_cog(API_Vendor(client))
    client.add_cog(Intercom(client))


#########################################
###### Registering Client Events ########
#########################################


@client.event # register the event that THE BOT IS READY
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


# @client.event # register the event when a A MESSAGE IS SENT, but not if the message is from itself (the bot)
# async def on_message(message):
#
#   if message.author == client.user: # if message is from the bot, return
#    return


#########################################
########## Run Discord Instance #########
#########################################

client.loop.create_task(setup()) # this will run when the bot is ready
client.run(os.getenv('TOKEN')) # runs the bot
