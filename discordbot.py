# This script is a combination of mini projects I have worked on and have integrated them into discords
# api so they can be accessed from different devices remotely.

import discord
import os
from discord.ext import commands, tasks
from itertools import cycle
import requests
from bs4 import BeautifulSoup


# setup
ID = "YOUR ID HERE"
token = "YOUR TOKEN HERE"
intents = discord.Intents.all()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix='.', intents=intents)
status = cycle(['Chess with Siri', 'Uno with Alexa'])


# startup sequence
@client.event
async def on_ready():
    change_status.start()
    print("Bot Started")


# activity loop
@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


# error checker
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please fill out all the arguments')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the right permissions so use this command")


# ping command
@client.command()
async def ping(ctx):
    await ctx.send('pong')


# hunt (sherlock.py script must be in same directory) (e.g. "hunt fakeuseraccount123")
# this will return a list of URLs containing the searched username from popular sites using the sherlock script
# sherlock.py is open source and can be found here "https://github.com/sherlock-project/sherlock"
# BE CAREFUL! Popular usernames such as "jack" will have 1,000s of accounts and can crash bot, so be specific
@client.command()
@commands.guild_only()
@commands.is_owner()
async def hunt(ctx, username):
    await ctx.send("searching for " + username + ", this might take a sec")
    os. system('sherlock.py --timeout 1 ' + username)
    file = open(username + ".txt", "r")
    text = file.read()
    await ctx.send(text)
    text.close()


# purge command (e.g. "purge 100")
@client.command(pass_context=True)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    await ctx.send('Chat has been purged by {}'.format(ctx.author.mention))
    await ctx.message.delete()
# purge error
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permissions to do that")


# kicking/banning
@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    amount = 1
    await member.kick(reason=reason)
    await ctx.channel.purge(limit=amount)
@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    amount = 1
    await member.ban(reason=reason)
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'Banned {member.mention}')
@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return
@client.command()
async def bans(ctx):
    banned_users = await ctx.guild.bans()
    await ctx.send(banned_users)


# weather
@client.command()
async def weather(ctx):
    await ctx.send("https://www.metoffice.gov.uk/weather/forecast/gcenyebhd")

# website code scraper (e.g. "scrape https://www.google.com 50")
# this will output the html contents of line 50
@client.command()
@commands.guild_only()
@commands.is_owner()
async def scrape(ctx, url, line):
    await ctx.send("processing")
    url1 = requests.get(url)
    soup = BeautifulSoup(url1.content, 'html.parser')
    text = open("boi.txt", "w")
    text.write(soup.prettify())
    text.close()
    mylines = []
    lineNumber = int(line)
    with open('boi.txt', 'rt') as myfile:
        for myline in myfile:
            mylines.append(myline)
    end = (mylines[lineNumber])
    await ctx.send("line " + line + " is")
    await ctx.send('"' + end + '"')


# website html word finder (e.g. "find https://www.google.com email")
# this will find what lines in the html contain "email"
@client.command()
@commands.guild_only()
@commands.is_owner()
async def find(ctx, url, word):
    await ctx.send("searching for " + word)
    url1 = requests.get(url)
    soup = BeautifulSoup(url1.content, 'html.parser')
    text = open("boi.txt", "w")
    text.write(soup.prettify())
    text.close()
    line_number = 0
    results = []
    with open("boi.txt", "r") as read_obj:
        for line in read_obj:
            line_number +=1
            if word in line:
                results.append(line_number - 1)
    await ctx.send("Found results on line")
    await ctx.send(results)

# script that retreives the temperature and humidity from a HTU21D sensor
import board
from adafruit_htu21d import HTU21D
@client.command()
@commands.guild_only()
async def temp_sensor(ctx):
    i2c = board.I2C()
    sensor = HTU21D(i2c)
    await ctx.send("Getting information on User's Room...")
    await ctx.send("Temperature is: %0.1f C" % sensor.temperature)
    await ctx.send("Humidity is: %0.1f %%" % sensor.relative_humidity)
@client.command()
@commands.guild_only()

# this script gets data from a local webserver that contain temp and humidity storaged on html lines 15 and 18
async def temp_local(ctx):
    await ctx.send("Getting information on Other User's Room...")
    url = "http://192.168.1.1:1000" # change this to the IP
    line1 = 15 # this is the line
    line2 = 18
    url1 = requests.get(url)
    soup = BeautifulSoup(url1.content, 'html.parser')
    text = open("boi.txt", "w")
    text.write(soup.prettify())
    text.close()
    mylines = []
    lineNumber = int(line1)
    with open('storage.txt', 'rt') as myfile:
        for myline in myfile:
            mylines.append(myline)
    end = (mylines[lineNumber])
    await ctx.send(end)
    lineNumber = int(line2)
    with open('storage.txt', 'rt') as myfile:
        for myline in myfile:
            mylines.append(myline)
    end = (mylines[lineNumber])
    await ctx.send(end)


# terminates the script remotely
# CANNOT BE RESTARTED REMOTELY (unless second bot is active)
@client.command()
@commands.guild_only()
@commands.is_owner()
async def END(ctx):
    await ctx.send("Terminating Script")
    print("Script Ended")
    exit()

client.run(token)
