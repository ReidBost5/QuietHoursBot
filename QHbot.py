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

@bot.event
async def on_ready():

    print(f'Bot is running')

    try:

        synced = await bot.tree.sync()

    except Exception as e:

        print(e)

#getters and setters for global Variables (Log Channel ID, Roles Excempt from Quiet Hours, etc.)
def setLog(ID):

    ID = (str)(ID)
    f = open("information.txt", "w")
    f.write(ID)
    f.close()

def getLogChannel():

    f = open("information.txt", "r")
    ID = f.readline()
    f.close()

    return ID

def setHours(tz, startHour, endHour):
    pass

def getEndHour():
    pass

def getStartHour():
    pass

#bot commands
@bot.tree.command(name = "setup")
@app_commands.describe(log = "Log Channel", start = "Start time of quiet hours (ex: 12am)", end = "End time of quiet hours (ex: 12am)", tz = "timezone (ex: EST, CST, PST)")
async def setup(interaction: discord.Interaction, log: discord.TextChannel, start: str, end: str, tz: str = "utc"):

    if interaction.user.guild_permissions.administrator:

        log = log.id

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

    logs_channel = await bot.fetch_channel(getLogChannel())

    if ctx.author != bot.user:
        msgTime = ctx.created_at
        msgTime = msgTime.strftime("%H")

        if int(msgTime) > 0:

            await logs_channel.send(f"{ctx.author} sent the message: \"{ctx.content}\" at {msgTime}")


bot.run(TOKEN)