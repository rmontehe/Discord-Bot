import discord
import json # work with json files
import os
import requests # allows our module to make an HTTP request to get data from the API
from discord.ext import commands
from dotenv import load_dotenv # python library that allows you to load variables from a .env file


load_dotenv() # loads the .env variables to the

class API_Vendor(commands.Cog): # declare a class named API_Vendor
    def __init__(self, bot): # define initialization method
        self.bot = bot       # assign attribute of initialization as the input bot variables
        print("Initializing API Vendor...")

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

    @commands.command()
    async def joke(self,ctx):
        joke = API_Vendor.get_joke() # get a joke from the joke api
        await ctx.send(joke) # send a message to the channel that contains a joke

    @commands.command()
    async def roastme(self,ctx):
        roast = API_Vendor.get_roast() # get a roast from evil insult generator API
        await ctx.send(roast) # send a message to the channel that contains a roast
