import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession
from main import champDict

class Tier(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Tier cog is online.')

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tier(self, ctx):
        res = await self.session.get('https://www.op.gg/champion/statistics')
        table = res.html.find('.champion-trend-tier-TOP')[0]
        champions = table.find('tr')[0:5]

        embed = discord.Embed(
            title='Champion Rankings (Overall)',
            color=self.color
        )

        for champion in champions:
            # info: [tierPos, tierChange, name, roles, winrate, pickrate]
            info = champion.text.split('\n')
            summaryStr = f'''
                Roles · **{info[3]}**
                Win Rate · **{info[4]}**
                Pick Rate · **{info[5]}**
            '''
            embed.add_field(name=f'{info[0]}. {champDict[info[2]]} {info[2]}', value=summaryStr, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wins(self, ctx):
        res = await self.session.get('https://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio')
        table = res.html.find('.champion-trend-winratio-ALL')[0]

        champions = table.find('tr')[0:5]

        embed = discord.Embed(
            title='Champion Rankings (by Win Rate)',
            color=self.color
        )

        for champion in champions:
            # info: [tierPos, name, roles, winrate, pickrate]
            info = champion.text.split('\n')
            summaryStr = f'''
                Roles · **{info[2]}**
                Win Rate · **{info[3]}**
                Pick Rate · **{info[4]}**
            '''
            embed.add_field(name=f'{info[0]}. {champDict[info[1]]} {info[1]}', value=summaryStr, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def picks(self, ctx):
        res = await self.session.get('https://www.op.gg/champion/ajax/statistics/trendChampionList/type=pickratio')
        table = res.html.find('.champion-trend-pickratio-ALL')[0]

        champions = table.find('tr')[0:5]

        embed = discord.Embed(
            title='Champion Rankings (by Pick Rate)',
            color=self.color
        )

        for champion in champions:
            # info: [tierPos, name, roles, pickrate, winrate]
            info = champion.text.split('\n')
            summaryStr = f'''
                Roles · **{info[2]}**
                Pick Rate · **{info[3]}**
                Win Rate · **{info[4]}**
            '''
            embed.add_field(name=f'{info[0]}. {champDict[info[1]]} {info[1]}', value=summaryStr, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bans(self, ctx):
        res = await self.session.get('https://www.op.gg/champion/ajax/statistics/trendChampionList/type=banratio')
        table = res.html.find('.champion-trend-banratio-ALL')[0]

        champions = table.find('tr')[0:5]

        embed = discord.Embed(
            title='Champion Rankings (by Ban Rate)',
            color=self.color
        )

        for champion in champions:
            # info: [tierPos, name, roles, banrate]
            info = champion.text.split('\n')
            summaryStr = f'''
                Roles · **{info[2]}**
                Ban Rate · **{info[3]}**
            '''
            embed.add_field(name=f'{info[0]}. {champDict[info[1]]} {info[1]}', value=summaryStr, inline=False)
        

        await ctx.send(embed=embed)
    
def setup(client):
    client.add_cog(Tier(client))

# todo: allow ordering within roles
