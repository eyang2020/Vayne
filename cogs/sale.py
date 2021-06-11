import os
import pymongo
import discord
from discord.ext import commands
from datetime import datetime
from requests_html import AsyncHTMLSession

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)

db = cluster.test
collectionUserToSkin = db['UserToSkin']
collectionSkinToUser = db['SkinToUser']

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

    @commands.command(aliases=['wl'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wishlist(self, ctx):
        user = ctx.message.author
        userId = user.id
        embed = discord.Embed(
            color=self.color
        )

        doc = collectionUserToSkin.find_one({'userId': userId})
        skins = doc['skins']

        skinStr = '```ml\n'
        for skin in skins:
            skinStr += f'{skin}\n'
        skinStr += '```'

        embed.add_field(name='Wishlisted Skins', value=skinStr, inline=False)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
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

# todo: add skin wishlist / notification system (through dm)
