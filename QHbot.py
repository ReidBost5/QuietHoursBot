import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from datetime import timedelta, timezone, datetime
import pytz
from typing import Literal, Union, NamedTuple
from dateutil.tz import gettz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix = '.qh ', intents = discord.Intents.all(), help_command = None)

#Global Variables (server names and timezone offset)
guildname = None
estTimeDelta = timedelta(hours = -5)
cstTimeDelta = timedelta(hours = -6)
mtTimeDelta = timedelta(hours = -7)
pstTimeDelta = timedelta(hours = -8)
utcTimeDelta = timedelta(hours = 0)

@bot.event
async def on_ready():

    print(f'Bot is running')

    try:

        synced = await bot.tree.sync()
        print("bot is synced")

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

            log = ID[13:]

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
    
    f = open("%s.txt" % guildname, "r")

    ID = None

    while ID != '':

        ID = f.readline()
        index = ID.find("End Time: ")

        if index != -1:

            end = ID[10:]

    f.close()

    if 'pm' in end and '12' not in end:
        end = end[:-3]
        end24Time = int(end) + 12
    else:
        end = end[:-3]
        end24Time = int(end)

    return end24Time

def getStartHour():
    
    f = open("%s.txt" % guildname, "r")

    ID = None

    while ID != '':

        ID = f.readline()
        index = ID.find("Start Time: ")

        if index != -1:

            start = ID[12:]

    f.close()

    if 'pm' in start and '12' not in start:
        start = start[:-3]
        start24Time = int(start) + 12
    else:
        start = start[:-3]
        start24Time = int(start)

    return start24Time

def getTimezone():
    
    f = open("%s.txt" % guildname, "r")

    ID = None

    while ID != '':

        ID = f.readline()
        index = ID.find("Timezone: ")

        if index != -1:

            tz = ID[10:]

    f.close()

    tz = tz.rstrip()

    return tz

def setRole(roleID):
    
    f = open("%s.txt" % guildname, "a")
    f.write(f"Role ID: {roleID}\n")
    f.close()

def getRole():

    role = 0

    f = open("%s.txt" % guildname, "r")

    ID = None

    while ID != '':

        ID = f.readline()
        index = ID.find("Role ID: ")

        if index != -1:

            role = ID[8:]

    f.close()

    return int(role)

#returns true if currentTime is within quiet hours, false otherwise
def checkTime(start, end, currentTime):
    
    if end < start:

        if currentTime <= end or currentTime >= start:

            return True
        
        else:

            return False
        
    else:

        if start <= currentTime <= end:

            return True
        
        else:

            return False

#bot commands
@bot.tree.command(name = "setup")
@app_commands.describe(log = "Log Channel", start = "Start time of quiet hours (ex: 12am)", end = "End time of quiet hours (ex: 12am)", timezones = "timezone (ex: EST, CST, PST, MST)")
@app_commands.choices(timezones = [app_commands.Choice(name = "Eastern", value = "EST"), app_commands.Choice(name = "Central", value = "CST"), app_commands.Choice(name = "Pacific", value = 'PST'), app_commands.Choice(name = "Mountain", value = "MT")])
async def setup(interaction: discord.Interaction, log: discord.TextChannel, start: str, end: str, timezones: app_commands.Choice[str], role: discord.Role):

    if interaction.user.guild_permissions.administrator:

        if 'am' not in start and 'pm' not in start or 'am' not in end and 'pm' not in end:

            await interaction.response.send_message(f'ERROR: am or pm not included. Make sure time values end with am or pm. **Ex: 1am**')

        else:

            setGuildname(interaction.guild)
            if os.path.exists("%s.txt" % guildname):

                os.remove("%s.txt" % guildname)
            
            setRole(role.id)

            log = log.id
            setLog(log)
            logs_channel = await bot.fetch_channel(getLogChannel())

            tz = timezones.value
            setHours(tz, start, end)

            await interaction.response.send_message(f"Setup Complete!\n--------------------\nLogs Channel: {logs_channel}\nTimezone: {tz}\n\
Quiet Hours Start Time: {start}\nQuiet Hours End Time: {end}\nRole Affected: {role}\n--------------------")

    else:

        await interaction.response.send_message("You do not have access to this command", ephemeral = True)

@bot.event
async def on_message(ctx):

    global guildname
    guildname = ctx.guild.name

    if ctx.author.get_role(getRole()) != None:

        logs_channel = await bot.fetch_channel(getLogChannel())

        if ctx.author != bot.user:
            
            zone = getTimezone()

            if zone == 'EST':
                zone = estTimeDelta
            elif zone == 'CST':
                zone = cstTimeDelta
            elif zone == 'MST':
                zone = mtTimeDelta
            elif zone == 'PST':
                zone = pstTimeDelta
            else:
                zone = utcTimeDelta  

            msgTime = ctx.created_at 
            msgTime = msgTime.replace(tzinfo = pytz.utc).astimezone(timezone(zone))
            msgHour = msgTime.strftime("%H")
            msgTime = msgTime.strftime("%I:%M%p")
            
            if msgTime[0] == '0':

                msgTime = msgTime[1:]

            if checkTime(getStartHour(), getEndHour(), int(msgHour)):

                await logs_channel.send(f"{ctx.author} sent the message: \"{ctx.content}\" at {msgTime}")
                await ctx.delete()

bot.run(TOKEN)