# import relevant python libraries
import discord
import json # work with json files
import os
import requests # allows our module to make an HTTP request to get data from the API
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv # python library that allows you to load variables from a .env file
from music import Player

load_dotenv() # loads the .env variables to the

client = commands.Bot(command_prefix = '!')  # create an instance of a client, the connection to Discord


#########################################
########## Defining Functions ###########
#########################################

def get_joke(): # returns a joke from the joke api

    response = requests.get(os.getenv("JOKE_API")) # requests for joke from the joke API
    json_data = json.loads(response.text) # convert the response into json format

    if json_data["type"] == "twopart": # if the joke is a two-part joke
        setup = json_data["setup"]
        punchline = json_data["delivery"]
        joke = setup + "\n" + punchline
        return(joke)

    else:   # if the joke is a single-part joke
        joke = json_data["joke"]
        return(joke)


def get_roast(): # returns a roast from the evil insult generator api
    response = requests.get(os.getenv('ROAST_API')) # requests for roast from the evil insult generator API
    json_data = json.loads(response.text) # convert the response into json format
    roast = json_data["insult"] # assign the "insult" value to roast instance
    return(roast)

async def setup():
    await client.wait_until_ready()
    client.add_cog(Player(client))


#########################################
########## Defining Commands ############
#########################################

@client.command()
async def joke(ctx):
    joke = get_joke() # get a joke from the joke api
    await ctx.send(joke) # send a message to the channel that contains a joke

@client.command()
async def roastme(ctx):
    roast = get_roast() # get a roast from evil insult generator API
    await ctx.send(roast) # send a message to the channel that contains a roast

@client.command()
async def is_connected(ctx):
    isConnected = ctx.voice_client.is_connected()
    await ctx.send(isConnected)
#### This is_connected command evaluated whether or not Beep Boop was connected to a Channel
#### When Beep Boop was in a voice channel, it returned True
#### However when Beep Boop was not in a channel, it returned and error, because beep boop was not in a channel
#### and the Value was None-type value, and a None-type value does not have attribute/method "is_connected()"

@client.command()
async def is_BotPlaying(ctx):
    isPlaying = ctx.voice_client.is_playing()
    await ctx.send(isPlaying)


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
