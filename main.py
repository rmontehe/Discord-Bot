# import relevant python libraries
import discord
import os
import requests # allows our module to make an HTTP request to get data from the API
import json # work with json files
from dotenv import load_dotenv # python library that allows you to load variables from a .env file

load_dotenv() # loads the .env variables to the

client = discord.Client() # create an instance of a client, the connection to Discord

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
###### Registering Client Events ########
#########################################


@client.event # register the event that THE BOT IS READY
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event # register the event when a A MESSAGE IS SENT, but not if the message is from itself (the bot)
async def on_message(message):

  if message.author == client.user: # if message is from the bot, return
   return

  if message.content.startswith('$joke'):   #if message received starts with '$joke'
    joke = get_joke()
    await message.channel.send(joke)     # send a message to the channel that says a joke returned by the method

  elif message.content.startswith('$roastme'):   #if message received starts with '$hello'
    roast = get_roast()
    await message.channel.send(roast)     # send a message to the channel that says a roast returned by the method

# runs the bot
# input is the bot's token, like the password for activating the bot
client.run(os.getenv('TOKEN'))
