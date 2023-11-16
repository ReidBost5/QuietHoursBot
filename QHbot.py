import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from datetime import timedelta, timezone
import pytz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix = '.qh ', intents = discord.Intents.all(), help_command = None)

# Global Variables (server name and timezone offset)
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

# Getters and Setters for global Variables (Log Channel ID, Roles Excempt from Quiet Hours, etc.)
def setGuildname(servername):

    global guildname
    guildname = servername

# Converting log_channel ID to str and storing it in file with server name
def setLog(ID):

    ID = (str)(ID)
    f = open("%s.txt" % guildname, "a")
    f.write(f"Log Channel: {ID}\n")
    f.close()

# Searches file and retrieves log_channel
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

# Stores start time, end time, and timezone in file with server name
def setHours(tz, startHour, endHour):
    
    start = (str)(startHour)
    timezone = (str)(tz)
    end = (str)(endHour)

    f = open("%s.txt" % guildname, "a")
    f.write(f"Start Time: {start}\n")
    f.write(f"End Time: {end}\n")
    f.write(f"Timezone: {timezone}\n")
    f.close()

# Searches file and retrieves end hour, converts it to an integer and into 24 hour time to be used for comparisons
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

# Searches file and retrieves start hour, converts it to an integer and into 24 hour time to be used for comparisons
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

# Searches file and retrieves timezone
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

# Stores role ID in file with server name
def setRole(roleID):
    
    f = open("%s.txt" % guildname, "a")
    f.write(f"Role ID: {roleID}\n")
    f.close()

# Searches file and retrieves role ID
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

# Returns true if currentTime is within quiet hours, false otherwise
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

# Bot commands
@bot.tree.command(name = "setup")
@app_commands.describe(log = "Log Channel", start = "Start time of quiet hours (ex: 12am)", end = "End time of quiet hours (ex: 12am)", timezones = "timezone (ex: EST, CST, PST, MST)")
@app_commands.choices(timezones = [app_commands.Choice(name = "Eastern", value = "EST"), app_commands.Choice(name = "Central", value = "CST"), app_commands.Choice(name = "Pacific", value = 'PST'), app_commands.Choice(name = "Mountain", value = "MT")])
async def setup(interaction: discord.Interaction, log: discord.TextChannel, start: str, end: str, timezones: app_commands.Choice[str], role: discord.Role):

    # Checks if user is admin, if they are then command is ran, otherwise responds with access denied message
    if interaction.user.guild_permissions.administrator:

        # Checks if start and end time has am or pm in them, otherwise returns an error message and command needs to be rerun
        if 'am' not in start and 'pm' not in start or 'am' not in end and 'pm' not in end:

            await interaction.response.send_message(f'ERROR: am or pm not included. Make sure time values end with am or pm. **Ex: 1am**')

        else:

            # Sets server name global variable to current server, if a file named after this server exists then file is deleted and replaced with setup info
            setGuildname(interaction.guild)
            if os.path.exists("%s.txt" % guildname):

                os.remove("%s.txt" % guildname)
            
            # Setting Role, Log, and Time Info
            setRole(role.id)

            setLog(log.id)
            logs_channel = await bot.fetch_channel(getLogChannel())

            tz = timezones.value
            setHours(tz, start, end)

            # Response
            await interaction.response.send_message(f"Setup Complete!\n--------------------\nLogs Channel: {logs_channel}\nTimezone: {tz}\n\
Quiet Hours Start Time: {start}\nQuiet Hours End Time: {end}\nRole Affected: {role}\n--------------------")

    else:

        # Sent if user is not admin
        await interaction.response.send_message("You do not have access to this command", ephemeral = True)

@bot.event
async def on_message(ctx):

    # Sets global variable to server name where message was sent
    global guildname
    guildname = ctx.guild.name

    # Checks if author has role that is affected by Quiet Hours
    if ctx.author.get_role(getRole()) != None:

        logs_channel = await bot.fetch_channel(getLogChannel())

        # Makes sure bot doesnt affects it's own messages
        if ctx.author != bot.user:
            
            # Gets timezone and finds which time delta to use
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

            # Gets time data from message, converts it to correct timezone (from utc), creates msgHour and stores hour to be used for comparison, 
            # Creates a string called msgTime to be used for output in log channel
            msgTime = ctx.created_at 
            msgTime = msgTime.replace(tzinfo = pytz.utc).astimezone(timezone(zone))
            msgHour = msgTime.strftime("%H")
            msgTime = msgTime.strftime("%I:%M%p")
            
            # Removes 0 from start of certain times (ex. 01:00pm --> 1:00pm)
            if msgTime[0] == '0':

                msgTime = msgTime[1:]

            # Checks if time is within quiet hours, if so logs message with user, content, and time info and then deletes the message
            if checkTime(getStartHour(), getEndHour(), int(msgHour)):

                await logs_channel.send(f"{ctx.author} sent the message: \"{ctx.content}\" at {msgTime}")
                await ctx.delete()

bot.run(TOKEN)