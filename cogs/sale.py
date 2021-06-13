import os
import pymongo
import discord
from discord.ext import commands, tasks
from datetime import datetime
from requests_html import AsyncHTMLSession

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)

db = cluster.test
collectionUserToSkin = db['UserToSkin']
collectionSkinToUser = db['SkinToUser']
collectionSaleInfo = db['SaleInfo']

class Sale(commands.Cog):

    # saleCache: cache for current sale. format: {itemName: (fullPrice, discountPrice)}
    # durationCache: current sale duration
    saleCache = {}
    durationCache = ''
    
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()
        self.checkSale.start()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Sale cog is online.')

    def cog_unload(self):
        self.checkSale.cancel()

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Tasks
    @tasks.loop(hours=24)
    async def checkSale(self):
        print('Checking for new sale...')
        #print(self.saleCache)
        res = await self.session.get('https://leagueoflegends.fandom.com/wiki/Sales')
        curDuration = res.html.xpath('//*[@id="onsale"]/div/div[1]/text()')[0]
        docSaleInfo = collectionSaleInfo.find_one({'saleInfo': 'saleInfo'})
        storedDuration = docSaleInfo['duration']
        # check on whether a new sale as begun or if cache needs to be initialized
        newSale = (curDuration != storedDuration)
        if newSale or not self.saleCache:
            # update cache
            self.saleCache = {}
            res = await self.session.get('https://leagueoflegends.fandom.com/wiki/Sales')
            table = res.html.xpath('//*[@id="onsale"]/div/div[2]')[0]
            banners = table.find('.centered-grid-icon')
            for banner in banners:
                info = banner.text.split('\n')
                self.saleCache[info[0]] = (info[1], info[2])
            self.durationCache = curDuration
            # if there is a new sale: update db and send a round of dm's to notify wishlist
            if newSale: 
                # update db
                collectionSaleInfo.update_one({'saleInfo': 'saleInfo'}, {'$set': {'duration': curDuration}}, upsert=True)
                # for each skin, dm the users who have it wishlisted
                for itemName, priceTuple in self.saleCache.items():
                    docSkinToUser = collectionSkinToUser.find_one({'skin': itemName})
                    if not docSkinToUser:
                        # if no doc was found, this was a champion on sale
                        continue
                    userIds = docSkinToUser['userId']
                    if len(userIds) == 0:
                        continue
                    # create the embed
                    embed = discord.Embed(
                        color=self.color
                    )
                    formattedStr = f'```ml\n{itemName} {priceTuple[0]} → {priceTuple[1]}```\n'
                    embed.add_field(name='A skin you wishlisted is on sale!', value=formattedStr, inline=False)
                    for userId in userIds:
                        user = self.client.get_user(userId)
                        await user.send(embed=embed)

        print('Finished checking for sale.')
        #print(self.saleCache)

    @checkSale.before_loop
    async def beforeCheckSale(self):
        await self.client.wait_until_ready()

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sale(self, ctx):
        if not self.saleCache:
            # fill cache
            res = await self.session.get('https://leagueoflegends.fandom.com/wiki/Sales')
            self.durationCache = res.html.xpath('//*[@id="onsale"]/div/div[1]/text()')[0]
            table = res.html.xpath('//*[@id="onsale"]/div/div[2]')[0]
            banners = table.find('.centered-grid-icon')
            for banner in banners:
                info = banner.text.split('\n')
                self.saleCache[info[0]] = (info[1], info[2])
        # create embed
        durationStr = '```'
        championSaleStr = '```ml\n'
        skinSaleStr = '```ml\n'
        counter = 0
        # sale format: 5 champions first, then 15 skins
        for itemName, priceTuple in self.saleCache.items():
            formattedStr = f'{itemName:<30} {priceTuple[0]:>4} → {priceTuple[1]:>4}\n'
            if counter < 5: championSaleStr += formattedStr
            else: skinSaleStr += formattedStr
            counter += 1
        durationStr += self.durationCache

        durationStr += '```'
        championSaleStr += '```'
        skinSaleStr += '```'

        embed = discord.Embed(
            title='Current Sale',
            color=self.color
        )
        embed.add_field(name='Duration', value=durationStr, inline=False)
        embed.add_field(name='Champions', value=championSaleStr, inline=False)
        embed.add_field(name='Skins', value=skinSaleStr, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(aliases=['wl'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wishlist(self, ctx):
        user = ctx.message.author
        userId = user.id
        embed = discord.Embed(
            color=self.color
        )

        # todo: add support for case when doc is None
        doc = collectionUserToSkin.find_one({'userId': userId})
        skins = doc['skins']
        wishlistSize = len(skins)

        skinStr = '```ml\n'
        for skin in skins:
            if skin in self.saleCache:
                skinStr += f'{skin} (ON SALE)\n'
            else:
                skinStr += f'{skin}\n'
        skinStr += '```'

        embed.add_field(name='Wishlisted Skins', value=skinStr, inline=False)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text=f'{10 - wishlistSize}/10 slots available')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(aliases=['wa'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wishadd(self, ctx, *, query=None):
        user = ctx.message.author
        userId = user.id
        if not query:
            await ctx.send(f'{user.mention}, please enter a skin.')
            return

        skinDisplayName = ' '.join(w.capitalize() for w in query.split())
        query = skinDisplayName.replace(' ', '-')
        #print(query)

        res = await self.session.get(f'https://lolskinshop.com/product/{query}/')
        # check if the query is a valid skin
        if 'Page not found' in res.html.xpath('/html/head/title')[0].text:
            await ctx.send(f'{user.mention}, I could not find that skin.')
            return

        # check if skin is already on wishlist
        doc = collectionUserToSkin.find_one({'userId': userId})
        skins = doc['skins']
        wishlistSize = len(skins)

        # check wishlist size
        if wishlistSize >= 10:
            await ctx.send(f'{user.mention}, your wishlist is full.')
            return

        if skinDisplayName in skins:
            await ctx.send(f'{user.mention}, this skin is already on your wishlist.')
            return

        # update database
        collectionUserToSkin.update_one({'userId': userId}, {'$addToSet': {'skins': skinDisplayName}}, upsert = True)
        collectionSkinToUser.update_one({'skin': skinDisplayName}, {'$addToSet': {'userId': userId}}, upsert = True)

        # get champion skin banner
        img = res.html.find('.detailed-product-left')[0].find('img')[0].attrs['src']

        embed = discord.Embed(
            description=f'`{skinDisplayName}`\nhas been added to your wishlist.',
            color=self.color
        )
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_image(url=img)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(aliases=['wr'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wishremove(self, ctx, *, query):
        user = ctx.message.author
        userId = user.id
        if not query:
            await ctx.send(f'{user.mention}, please enter a skin.')
            return
        skinDisplayName = ' '.join(w.capitalize() for w in query.split())

        docUserToSkin = collectionUserToSkin.find_one({'userId': userId})
        skins = docUserToSkin['skins']

        if skinDisplayName in skins:
            collectionUserToSkin.update_one({'userId': userId}, {'$pull': {'skins': skinDisplayName}})
            collectionSkinToUser.update_one({'skin': skinDisplayName}, {'$pull': {'userId': userId}})
            await ctx.send(f'{user.mention}, `{skinDisplayName}` has been removed from your wishlist.')
        else:
            await ctx.send(f'{user.mention}, this skin is not on your wishlist.')

def setup(client):
    client.add_cog(Sale(client))

# todo: add emotes for all champions (big yikes)
