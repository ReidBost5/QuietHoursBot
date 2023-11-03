import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix = '.ff ', intents = discord.Intents.all(), help_command = None)

guildname = None

@bot.event
async def on_ready():

    print(f'Bot is running')

    try:

        synced = await bot.tree.sync()

    except Exception as e:

        print(e)

#getters and setters for global Variables (Log Channel ID, Roles Excempt from Quiet Hours, etc.)
def setGuildname(servername):

    global guildname
    guildname = servername

def setLog(ID):

    ID = (str)(ID)
    f = open("%s.txt" % guildname, "a")
    f.write(f"Log Channel: {ID}\n")
    f.close()

def getLogChannel():

    f = open("%s.txt" % guildname, "r")

    ID = None

    while ID != '':

        ID = f.readline()
        index = ID.find("Log Channel: ")

        if index != -1:

            log = ID[12:]

    f.close()

    return log

def setHours(tz, startHour, endHour):
    
    start = (str)(startHour)
    timezone = (str)(tz)
    end = (str)(endHour)

    f = open("%s.txt" % guildname, "a")
    f.write(f"Start Time: {start}\n")
    f.write(f"End Time: {end}\n")
    f.write(f"Timezone: {timezone}\n")
    f.close()

def getEndHour():
    pass

def getStartHour():
    pass

#bot commands
@bot.tree.command(name = "setup")
@app_commands.describe(log = "Log Channel", start = "Start time of quiet hours (ex: 12am)", end = "End time of quiet hours (ex: 12am)", tz = "timezone (ex: EST, CST, PST)")
async def setup(interaction: discord.Interaction, log: discord.TextChannel, start: str, end: str, tz: str = "utc"):

    if interaction.user.guild_permissions.administrator:

        setGuildname(interaction.guild)

        log = log.id

        if os.path.exists("%s.txt" % guildname):

            os.remove("%s.txt" % guildname)

        setLog(log)

        logs_channel = await bot.fetch_channel(getLogChannel())

        setHours(tz, start, end)

        await interaction.response.send_message(f"Setup Complete!\n--------------------\nLogs Channel: {logs_channel}\nTimezone: {tz}\n\
Quiet Hours Start Time: {start}\nQuiet Hours End Time: {end}\n--------------------")

    else:

        await interaction.response.send_message("You do not have access to this command", ephemeral = True)
#how to send messages to logs channel
#logs_channel = await bot.fetch_channel(getLogChannel())
#await logs_channel.send(f" is for {logs_channel}")


#TODO: Adjust this to depend on Timezone, also fix setup command to include timezone and roles n such
@bot.event
async def on_message(ctx):

    global guildname
    guildname = ctx.guild.name

    logs_channel = await bot.fetch_channel(getLogChannel())

    if ctx.author != bot.user:

        msgTime = ctx.created_at
        msgTime = msgTime.strftime("%H")

        if int(msgTime) > 0:

            await logs_channel.send(f"{ctx.author} sent the message: \"{ctx.content}\" at {msgTime}")


bot.run(TOKEN)