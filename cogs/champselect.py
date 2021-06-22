import os
import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession
from main import champDict

RIOT_API_KEY = os.environ['RIOT_API_KEY']

class Summoner:
    def __init__(self, username):
        self.username = username
        self.rank = ''
        self.winrate = ''
        self.wonCnt = ''
        self.lossCnt = ''
        self.mostPlayedPosition = ''
        self.mainChampion = ''

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

        if len(lines) == 1:
            line = lines[0]
            try:
                username = line[:line.index('joined the lobby')]
            except:
                username = line
            # single-summoner loopup

            queryUrl = f'https://na.op.gg/summoner/userName={username}'
            res = await self.session.get(queryUrl)
            profileIconUrl = 'https:' + res.html.find('body > div.l-wrap.l-wrap--summoner > div.l-container > div > div > div.Header > div.Face > div > img')[0].attrs['src']
            cleanUsername = res.html.find('body > div.l-wrap.l-wrap--summoner > div.l-container > div > div > div.Header > div.Profile > div.Information > span')[0].text
            rankInfo = res.html.find('#SummonerLayoutContent > div.tabItem.Content.SummonerLayoutContent.summonerLayout-summary > div.SideContent > div.TierBox.Box > div > div.TierRankInfo')[0]
            rankType = rankInfo.find('.RankType')[0].text
            rankTier = rankInfo.find('.TierRank')[0].text
            tierInfo = rankInfo.find('.TierInfo')[0]
            LP = tierInfo.find('.LeaguePoints')[0].text
            winLossInfo = tierInfo.find('.WinLose')[0]
            wins = winLossInfo.find('.wins')[0].text
            losses = winLossInfo.find('.losses')[0].text
            winratio = winLossInfo.find('.winratio')[0].text.split()[-1]
            championPool = res.html.xpath('//*[@id="SummonerLayoutContent"]/div[2]/div[1]/div[3]/div[2]/div[1]/div')[0].find('.ChampionBox')

            summaryStr = f'Summoner · **{cleanUsername}**\n{rankType} · **{rankTier}** ({LP})\nWin Ratio · **{winratio}** ({wins} | {losses})'

            embed = discord.Embed(
                title='Summoner Lookup',
                description=summaryStr,
                color=self.color
            )

            embed.set_thumbnail(url=profileIconUrl)

            championPoolStr = ''
            for champion in championPool:
                championInfo = champion.find('.ChampionInfo')[0].text.split('\n')
                name = championInfo[0]
                creepScore = championInfo[1]

                personalKDA = champion.find('.PersonalKDA')[0].text.split('\n')
                avg = personalKDA[0]
                '''
                # currently not used, but it splits average KDA into (k/D/A)
                components = personalKDA[1]
                '''
                playStats = champion.find('.Played')[0].text.split('\n')
                winrate = playStats[0]
                gamesPlayed = playStats[1]

                championPoolStr += f'{champDict[name]} `{winrate}` `{gamesPlayed}` `{avg}` `{creepScore}`\n'
            
            embed.add_field(name='Most Played Champions', value=championPoolStr, inline=False)
            
            await ctx.send(embed=embed)

        else:
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
                champions = res.html.find(f'body > div.l-wrap.l-wrap--multi > div.l-container > div.MultiSearchLayoutWrap > div > div.ContentWrap > div > div > ul > li:nth-child({i}) > div.most-champions-wrapper > ul.most-champions')[0].find('.most-champions__stats')

                '''
                for champion in champions:
                    print(champion.find('.champion')[0].attrs['title'])
                '''

                # todo: handle case when champ pool is empty
                mainChampion = champions[0].find('.champion')[0].attrs['title']

                summoners[i-1].rank = rank.text
                summoners[i-1].winrate = winrate.text
                summoners[i-1].wonCnt = gamesPlayed[0]
                summoners[i-1].lossCnt = gamesPlayed[1]
                summoners[i-1].mostPlayedPosition = position
                summoners[i-1].username = cleanUsername
                summoners[i-1].mainChampion = mainChampion

            embed = discord.Embed(
                title='Summoner Lookup',
                color=self.color
            )

            for summoner in summoners:
                summaryStr = f'{summoner.rank}\n{summoner.winrate} ({summoner.wonCnt} | {summoner.lossCnt})\n{summoner.mostPlayedPosition}'
                embed.add_field(name=f'{champDict[summoner.mainChampion]} {summoner.username}', value=summaryStr, inline=False)
            
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ChampSelect(client))

# todo: add error messages (could not find user) 
# todo: use async pillow to add rank border + level to profile icon
