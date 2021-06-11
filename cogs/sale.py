import discord
from discord.ext import commands
from datetime import datetime
from requests_html import AsyncHTMLSession

class Sale(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Sale cog is online.')

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sale(self, ctx):
        res = await self.session.get('https://leagueoflegends.fandom.com/wiki/Sales')
        durationStr = '```' + res.html.xpath('//*[@id="onsale"]/div/div[1]/text()')[0]
        table = res.html.xpath('//*[@id="onsale"]/div/div[2]')[0]
        banners = table.find('.centered-grid-icon')

        championSaleStr = '```ml\n'
        skinSaleStr = '```ml\n'
        counter = 0
        # sale format: 5 champions first, then 15 skins
        for banner in banners:
            info = banner.text.split('\n')
            formattedStr = f'{info[0]:<30} {info[1]:>4} → {info[2]:>4}\n'
            if counter < 5: championSaleStr += formattedStr
            else: skinSaleStr += formattedStr
            counter += 1

        championSaleStr += '```'
        skinSaleStr += '```'
        durationStr += '```'

        embed = discord.Embed(
            title='Current Sale',
            color=self.color
        )
        embed.add_field(name='Duration', value=durationStr, inline=False)
        embed.add_field(name='Champions', value=championSaleStr, inline=False)
        embed.add_field(name='Skins', value=skinSaleStr, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Sale(client))

# todo: add skin wishlist / notification system (through dm)
