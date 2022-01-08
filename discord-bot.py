# import relevant python libraries
import discord
from discord.ext import commands
import os
import requests # allows our module to make an HTTP request to get data from the API
import json # work with json files
from dotenv import load_dotenv # python library that allows you to load variables from a .env file

load_dotenv() # loads the .env variables to the

client = commands.Bot(command_prefix = '$')  # create an instance of a client, the connection to Discord


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
async def join(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to summon Beep Boop.")
    else: # if the user is in a voice channel
        voiceChannel = user.voice.channel # ID which voice channel the user is in
        await voiceChannel.connect(timeout=300) # connect to the voice channel that the user is in

@client.command()
async def disconnect(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to disconnect Beep Boop.")
    else: # if the user is in a voice channel
        await ctx.voice_client.disconnect() # disconnect from the current voice client

# @client.command()
# async def play()



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

client.run(os.getenv('TOKEN')) # runs the bot
