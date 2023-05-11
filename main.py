# import relevant python libraries
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv # python library that allows you to load variables from a .env file
from music import Player # import Player module from music file
from api import API_Vendor # import API_Vendor module from api file
from welcome import Intercom # import Intercom module from welcome file
from soundboard import Soundboard # import Soundboard module from soundboard file

load_dotenv() # loads the .env variables to the

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents = intents)  # create an instance of a client, the connection to Discord

#########################################
########## Defining Functions ###########
#########################################

async def setup():

    # when bot starts to run, run each module will run their own set up
    await client.wait_until_ready()
    client.add_cog(Player(client))
    client.add_cog(API_Vendor(client))
    client.add_cog(Intercom(client))
    client.add_cog(Soundboard(client))


#########################################
###### Registering Client Events ########
#########################################


@client.event # register the event that THE BOT IS READY
async def on_ready():
  print('We have logged in as {0.user}'.format(client)) # print to terminal that the screen name of the bot



#########################################
########## Run Discord Instance #########
#########################################

client.loop.create_task(setup()) # this will run when the bot is ready
client.run(os.getenv('TOKEN')) # runs the bot using the bot token obtained from Discord
                               # currently the TOKEN placeholder is '#####' in the .env file_name
                               # since this repositroy is public
                               # in most if not all scenarios it can be detrimental for bot
                               # developers if outside users were able to get ahold of the bot TOKEN
