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
    async def skill(self, ctx, champion=None, role=None): # todo: handle spaces. ex: miss fortune (w/wo role)
        user = ctx.message.author
        if champion:
            try:
                champion = champion.lower().capitalize()
                if role:
                    role = role.lower().capitalize()
                    res = await self.session.get(f'https://na.op.gg/champion/{champion}/statistics/{role}')
                else:
                    res = await self.session.get(f'https://na.op.gg/champion/{champion}/statistics/')
                # get role used in url (opgg will 'default' it if role is invalid)
                role = res.url.split('/')[-1].lower().capitalize()
                # todo: fix img for miss fortune
                table = res.html.find('.champion-skill-build__table')[0]
                img = f'https://opgg-static.akamaized.net/images/lol/champion/{champion}.png'
                skills = table.text.split('\n')[15:]
        
                embed = discord.Embed(
                    title=f'Recommended Skill Order for `{champion}` `{role}`',
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
                await ctx.send(f'{user.mention}, please enter a valid champion name.')    
        else:
            await ctx.send(f'{user.mention}, please specify a champion using **vskill [champion] [role]**.')
        
def setup(client):
    client.add_cog(Champion(client))
