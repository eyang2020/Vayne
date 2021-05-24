import os
import discord
import aiohttp
import asyncio
from discord.ext import commands
from datetime import datetime

RIOT_API_KEY = os.environ['RIOT_API_KEY']

class ChampSelect(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = aiohttp.ClientSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ChampSelect cog is online.')

    # Commands
    @commands.command(aliases=['lu'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lookup(self, ctx, *, info):
        embed = discord.Embed(
            title='Champion Select Overview',
            color=self.color
        )
        usernames = []

        lines = info.split('\n')
        for line in lines:
            usernames.append(line[:line.index('加入了队伍聊天')])
        usernameStr = ''
        usernameStr = ','.join(usernames)
        embed.add_field(name='\u2800', value=usernameStr, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

        # form the opgg multiquery url
        # https://na.op.gg/multi/query=AtomicAngel22%2CMuffintopper66%2Cthigh%20gap%20gg%2CWukumi%2CTheGamingFiles
        multiqueryUrl = f'https://na.op.gg/multi/query={"%2C".join(usernames)}'
        print(multiqueryUrl)
        async with aiohttp.ClientSession() as session:
            async with session.get(multiqueryUrl) as response:

                #print("Status:", response.status)
                #print("Content-type:", response.headers['content-type'])

                html = await response.text()
                print(html)
        
def setup(client):
    client.add_cog(ChampSelect(client))

# add option to set language (default is EN)
