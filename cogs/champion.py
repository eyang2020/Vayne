import discord
from discord.ext import commands
from datetime import datetime
from requests_html import AsyncHTMLSession

class Champion(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color = discord.Colour(0x5500ff)
        self.session = AsyncHTMLSession()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Champion cog is online.')

    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        await self.session.close()

    # Commands
    @commands.command(aliases=['s'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skill(self, ctx, *, query=None)
        user = ctx.message.author
        if query:
            try:
                #query = ''.join(query.split())
                query = query.lower().split('|')
                championDisplayName = query[0].strip().title()
                championSearchName = ''.join(championDisplayName.split())
                role = None
                # special case for jarvan iv
                if championDisplayName == 'Jarvan Iv':
                    championDisplayName = 'Jarvan IV'
                    championSearchName = 'JarvanIV'
                if len(query) > 1:
                    role = query[1].strip().capitalize()
                if role:
                    res = await self.session.get(f'https://na.op.gg/champion/{championSearchName}/statistics/{role}')
                else:
                    res = await self.session.get(f'https://na.op.gg/champion/{championSearchName}/statistics/')
                # get role used in url (opgg will 'default' it if role is invalid)
                role = res.url.split('/')[-1].lower().capitalize()
                table = res.html.find('.champion-skill-build__table')[0]
                img = f'https://opgg-static.akamaized.net/images/lol/champion/{championSearchName}.png'
                skills = table.text.split('\n')[15:]
                embed = discord.Embed(
                    title=f'Recommended Skill Order for `{championDisplayName}` `{role}`',
                    color=self.color
                )
                embed.set_thumbnail(url=img)
                
                skillStr = ''
                for i in range(1, 10): skillStr += f'`{i} ` '
                for i in range(10, 16): skillStr += f'`{i}` '
                skillStr += '\n'
                skillStr += ' '.join(f'`{skill} `' for skill in skills)

                embed.add_field(name='Skill Order', value=skillStr, inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed)
            except Exception as e:
                print(f'Error: {e}')
                await ctx.send(f'{user.mention}, I could not find a recommended skill build for this champion.')    
        else:
            await ctx.send(f'{user.mention}, please specify a champion using **vskill [champion] [role]**.')
        
def setup(client):
    client.add_cog(Champion(client))
