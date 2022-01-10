# import relevant python libraries
import discord
import json # work with json files
import os
import requests # allows our module to make an HTTP request to get data from the API
import youtube_dl
from discord.ext import commands
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
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice channel
        voiceChannel = user.voice.channel # ID which voice channel the user is in
        await voiceChannel.connect(timeout=300) # connect to the voice channel that the user is in

@client.command()
async def disconnect(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice channel
        voice = ctx.voice_client
        if voice is None: # if the bot is not in a channel
            await ctx.send("Beep Boop is not connected to a channel.")
        else: # if the bot is in a channel
            await ctx.voice_client.disconnect() # disconnect from the current voice channel

@client.command()
async def play(ctx, url : str): # parameter is a url, input type is a string
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice Channel
        voiceChannel = user.voice.channel # instance a variable containing the channel the user is in
        voice = ctx.voice_client # instantiate voice variable, what voice_client the bot is in
        if voice is None: # if the bot is not in a voice channel
            await voiceChannel.connect() # bot joins the voice channel that the user is in
            voice = ctx.voice_client # update voice variable since the bot joined the channel
        if voice != None and voice.is_playing(): # if the bot is
            voice.stop() # stops whatever is currently is playing
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} # handles the streaming in discord, standard preferences for streaming
        YDL_OPTIONS = {'format':"bestaudio"} # best audio format
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False) # extracts information from the youtube url, does not download the video
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            print(type(ctx.voice_client))
            voice.play(source=source)



@client.command()
async def pause(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice Channel
        voice = ctx.voice_client
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Beep Boop is not playing anything.")

@client.command()
async def resume(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice Channel
        voice = ctx.voice_client
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Beep Boop is not paused.")

@client.command()
async def stop(ctx):
    user = ctx.author # given the context we ID who the user is
    if user.voice == None: # if the user is not in a voice channel
        await ctx.send("Please join a Voice Channel to interact with Beep Boop.")
    else: # if the user is in a voice Channel
        voice.stop()



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

client.run(os.getenv('TOKEN')) # runs the bot
