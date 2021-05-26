import discord
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Settings cog is online.')

    # Commands
    @commands.command(aliases=['l', 'lang'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def language(self, ctx, language=None):
        # set language (default is EN)
        user = ctx.message.author
        if language:
            await ctx.send(f'{user.mention}, your language has been set to {language}.')
        else:
            await ctx.send(f'{user.mention}, please specify a language using **vlanguage [language]**.')

def setup(client):
    client.add_cog(Settings(client))
