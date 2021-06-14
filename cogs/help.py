import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Help cog is online.')

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(
            title='Commands for Vayne',
            description='Use **vhelp [command]** for more info on a command.',
            color=self.color
        )
        await ctx.send(embed=embed)
    
    '''
    # Temp Commands for Development (comment when unused)
    @commands.command()
    async def servers(self, ctx):
        activeservers = self.client.guilds
        for guild in activeservers:
            await ctx.send(guild.name)
            for emote in guild.emojis:
                print(f"'{emote.name}' : '<:{emote.name}:{emote.id}>',")
    '''

def setup(client):
    client.add_cog(Help(client))

# add option to set language (default is EN)
