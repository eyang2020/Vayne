import os
import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession

RIOT_API_KEY = os.environ['RIOT_API_KEY']

class Summoner:
    def __init__(self, username):
        self.username = username
        self.rank = ''
        self.winrate = ''
        self.wonCnt = ''
        self.lossCnt = ''
        self.mostPlayedPosition = ''

class ChampSelect(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ChampSelect cog is online.')

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Commands
    @commands.command(aliases=['lu'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lookup(self, ctx, *, info):
        summoners = []
        usernames = []
        lines = info.split('\n')
        for line in lines:
            #username = line[:line.index('加入了队伍聊天')]
            try:
                username = line[:line.index('joined the lobby')]
            except:
                username = line
            usernames.append(username)
            summoners.append(Summoner(username))
        summonerCnt = len(summoners)

        # op.gg returns data based on usernames (alphabetical order)
        # sort ignoring whitespace
        summoners.sort(key=lambda x: x.username.replace(' ', '').casefold())
    
        # form the opgg multiquery url
        # https://na.op.gg/multi/query=AtomicAngel22%2CMuffintopper66%2Cthigh%20gap%20gg%2CWukumi%2CTheGamingFiles
        multiqueryUrl = f'https://na.op.gg/multi/query={"%2C".join(usernames)}'
        #print(multiqueryUrl)
        res = await self.session.get(multiqueryUrl)
        # get info for each summoner
        for i in range(1, summonerCnt + 1):
            rank = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.summoner-summary > div.lp')[0]
            winrate = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.summoner-summary > div.graph > div > span')[0]
            gamesPlayed = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.summoner-summary > div.graph > div > div')[0]
            gamesPlayed = gamesPlayed.text.split('\n')
            position = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.summoner-summary > div.tier-position > div.most-position > i')[0].attrs['class'][1].split('most-position__icon--')[1]
            cleanUsername = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.summoner-summary > div.summoner-name > a')[0].text

            summoners[i-1].rank = rank.text
            summoners[i-1].winrate = winrate.text
            summoners[i-1].wonCnt = gamesPlayed[0]
            summoners[i-1].lossCnt = gamesPlayed[1]
            summoners[i-1].mostPlayedPosition = position
            summoners[i-1].username = cleanUsername

        embed = discord.Embed(
            title='Summoner Lookup',
            color=self.color
        )

        for summoner in summoners:
            summaryStr = f'{summoner.rank}\n{summoner.winrate} ({summoner.wonCnt} | {summoner.lossCnt})\n{summoner.mostPlayedPosition}'
            embed.add_field(name=summoner.username, value=summaryStr, inline=False)
        
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ChampSelect(client))

# todo: add error messages (could not find user) and individual vs multi-search
