import discord
from discord.ext import commands
from datetime import datetime
from requests_html import AsyncHTMLSession
from main import champDict

class ChampRotation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ChampRotation cog is online.')

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Commands
    @commands.command(aliases=['cr'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rotation(self, ctx):
        res = await self.session.get('https://leagueoflegends.fandom.com/wiki/Free_champion_rotation#Classic')
        durationStr = '```' + res.html.find('#rotationweek')[0].text
        championStr = ''

        champions = res.html.find('.free_champion_rotation')[0].text.split('\n')
        for champion in champions:
            championStr += f'{champDict[champion]}`{champion}`\n'

        durationStr += '```'

        embed = discord.Embed(
            title='Current Free Champion Rotation',
            color=self.color
        )
        embed.add_field(name='Duration', value=durationStr, inline=False)
        embed.add_field(name='Champions', value=championStr, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ChampRotation(client))

# todo: add cache support and daily check
