import os
import asyncio
import discord
import keep_alive
from datetime import datetime
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
client = commands.Bot(command_prefix=['v'], help_command=None, case_insensitive=True)
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
COG_FOLDER = os.path.join(THIS_FOLDER, 'cogs')

cdDict = {
    'help': [],
    'lookup': [],
    'language': [],
    'skill': []
}

# Commands
@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension=None):
    embed=discord.Embed(
        title='Cog Dashboard',
        color=discord.Colour(0x5500ff)
    )
    status = ''
    if extension is None:
        # reload all cogs
        client.dispatch('cog_unload_event')
        for fileName in os.listdir(COG_FOLDER):
            if fileName.endswith('.py'):
                extension = fileName[:-3]
                try:
                    client.unload_extension(f'cogs.{extension}')
                    client.load_extension(f'cogs.{extension}')
                    status += '✅`{}`\n'.format(extension)
                except:
                    status += '❌`{}`\n'.format(extension)
    else:
        # reload the specified cog
        try:
            if extension == 'champselect':
                client.dispatch('cog_unload_event')
            client.unload_extension(f'cogs.{extension}')
            client.load_extension(f'cogs.{extension}')
            status = '✅`{}`'.format(extension)
        except:
            status = '❌`{}`'.format(extension)
    # send report
    embed.add_field(name='\u2800', value=status, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

# cog init
for fileName in os.listdir(COG_FOLDER):
    if fileName.endswith('.py'):
        client.load_extension(f'cogs.{fileName[:-3]}')

# Events
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='vhelp'), status=discord.Status.online)
    print("Vayne is online.")

# Error Handling (Event)
@client.event
async def on_command_error(ctx, error):
    print(f'Error: {error}')
    # Cooldown Errors
    if isinstance(error, commands.CommandOnCooldown):
        user = ctx.message.author
        userId = user.id
        com = str(ctx.command).lower()
        if userId not in cdDict[com]:
            cdDict[com].append(userId)
            secondsLeft = round(error.retry_after)
            await ctx.send(f'{user.mention}, this command is on a `{secondsLeft} second` cooldown')
            await asyncio.sleep(secondsLeft)
            cdDict[com].remove(userId)

keep_alive.keep_alive()
client.run(TOKEN)
