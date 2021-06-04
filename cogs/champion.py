import discord
from discord.ext import commands
from datetime import datetime
from requests_html import AsyncHTMLSession

class Champion(commands.Cog):

    runeDict = {
        # Branches
        'Sorcery' : '<:Rune_Sorcery:850205314887450624>',
        'Resolve' : '<:Rune_Resolve:850205314828468284>',
        'Precision' : '<:Rune_Precision:850205314506817560>',
        'Inspiration' : '<:Rune_Inspiration:850215452789571656>',
        'Domination' : '<:Rune_Domination:850205315173449760>',

        # Sorcery
        'Summon Aery' : '',
        'Arcane Comet' : '',
        'Phase Rush' : '',

        'Nullifying Orb' : '',
        'Manaflow Band' : '',
        'Nimbus Cloak' : '',

        'Transcendence' : '',
        'Celerity' : '',
        'Absolute Focus' : '',

        'Scorch' : '',
        'Waterwalking' : '',
        'Gathering Storm' : '',

        # Resolve
        'Grasp of the Undying' : '<:Rune_Grasp_of_the_Undying:850216988394389545>',
        'Aftershock' : '<:Rune_Aftershock:850216987153006594>',
        'Guardian' : '<:Rune_Guardian:850216988324003881>',

        'Demolish' : '<:Rune_Demolish:850216988357296159>',
        'Font of Life' : '<:Rune_Font_of_Life:850216987895267349>',
        'Shield Bash' : '<:Rune_Shield_Bash:850216989040705556>',

        'Conditioning' : '<:Rune_Conditioning:850216987551858738>',
        'Second Wind' : '<:Rune_Second_Wind:850216988814999572>',
        'Bone Plating' : '<:Rune_Bone_Plating:850217261083918378>',

        'Overgrowth' : '<:Rune_Overgrowth:850216988428992563>',
        'Revitalize' : '<:Rune_Revitalize:850216988650504201>',
        'Unflinching' : '<:Rune_Unflinching:850216989397090345>',

        # Precision
        'Press the Attack' : '<:Rune_Press_the_Attack:850206475577458739>',
        'Lethal Tempo' : '<:Rune_Lethal_Tempo:850206474722607164>',
        'Fleet Footwork' : '<:Rune_Fleet_Footwork:850206474047324210>',
        'Conqueror' : '<:Rune_Conqueror:850206473732882442>',

        'Overheal' : '<:Rune_Overheal:850206474978066484>',
        'Triumph' : '<:Rune_Triumph:850206476806520893>',
        'Presence of Mind' : '<:Rune_Presence_of_Mind:850207617770455092>',

        'Legend: Alacrity' : '<:Rune_Legend__Alacrity:850206473970516000>',
        'Legend: Tenacity' : '<:Rune_Legend__Tenacity:850206474734927912>',
        'Legend: Bloodline' : '<:Rune_Legend__Bloodline:850206474319691778>',

        'Coup de Grace' : '<:Rune_Coup_de_Grace:850206473640607764>',
        'Cut Down' : '<:Rune_Cut_Down:850206473791602728>',
        'Last Stand' : '<:Rune_Last_Stand:850206474172104704>',

        # Glacial Augment
        'Glacial Augment' : '',
        'Unsealed Spellbook' : '',
        'Prototype: Omnistone' : '',
        'Hextech Flashtraption' : '',
        'Magical Footwear' : '',
        'Perfect Timing' : '',
        'Future\'s Market' : '',
        'Minion Dematerializer' : '',
        'Biscuit Delivery' : '',
        'Cosmic Insight' : '',
        'Approach Velocity' : '',
        'Time Warp Tonic' : '',

        # Domination
        'Electrocute' : '<:Rune_Electrocute:850214141969170452>',
        'Predator' : '<:Rune_Predator:850214144199360522>',
        'Dark Harvest' : '<:Rune_Dark_Harvest:850214141901406268>',
        'Hail of Blades' : '<:Rune_Hail_of_Blades:850214144221380609>',

        'Cheap Shot' : '<:Rune_Cheap_Shot:850214141788815360>',
        'Taste of Blood' : '<:Rune_Taste_of_Blood:850214143846907905>',
        'Sudden Impact' : '<:Rune_Sudden_Impact:850214144224264192>',

        'Zombie Ward' : '<:Rune_Zombie_Ward:850214143851495476>',
        'Ghost Poro' : '<:Rune_Ghost_Poro:850214144195428382>',
        'Eyeball Collection' : '<:Rune_Eyeball_Collection:850214144086114334>',

        'Ravenous Hunter' : '<:Rune_Ravenous_Hunter:850214144041025567>',
        'Ingenious Hunter' : '<:Rune_Ingenious_Hunter:850214144082575440>',
        'Relentless Hunter' : '<:Rune_Relentless_Hunter:850214144095158302>',
        'Ultimate Hunter' : '<:Rune_Ultimate_Hunter:850214143809945621>',

        # Fragment
        '' : '',
        '' : '',
        '' : ''
    }

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
    async def skill(self, ctx, *, query=None):
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
            await ctx.send(f'{user.mention}, please specify a champion using **vskill [champion] | (role)**.')
    
    @commands.command(aliases=['r'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rune(self, ctx, *, query=None):
        user = ctx.message.author
        if query:
            try:
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
                    res = await self.session.get(f'https://na.op.gg/champion/{championSearchName}/statistics/{role}/rune')
                else:
                    res = await self.session.get(f'https://na.op.gg/champion/{championSearchName}/statistics/x/rune')

                role = res.url.split('/')[-2].lower().capitalize()
                img = f'https://opgg-static.akamaized.net/images/lol/champion/{championSearchName}.png'

                tables = res.html.find('.perk-page')
                tableMain = tables[0]
                tableSecondary = tables[1]
                subtableMain = tableMain.find('img')
                subtableSecondary = tableSecondary.find('img')
                # fragment page (stat-runes)
                fragmentTable = res.html.find('.fragment-page')[0]
                fragmentMain = fragmentTable.find('img')

                runeMainStr = ''
                runeSecondaryStr = ''
                for rune in subtableMain:
                    if not 'grayscale' in rune.attrs['src']:
                        runeMainStr += self.runeDict[rune.attrs['title'][26:].split('</b>')[0]] + ' '

                for rune in subtableSecondary:
                    if not 'grayscale' in rune.attrs['src']:
                        runeSecondaryStr += self.runeDict[rune.attrs['title'][26:].split('</b>')[0]] + ' '

                #print(fragmentMain)
                for rune in fragmentMain:
                    if not 'grayscale' in rune.attrs['src']:
                        print(rune.attrs['title'].split('<span>')[1].split('</span>')[0])
                        

                embed = discord.Embed(
                    title=f'Recommended Runes for `{championDisplayName}` `{role}`',
                    color=self.color
                )
                embed.add_field(name='Primary', value=runeMainStr, inline=False)
                embed.add_field(name='Secondary', value=runeSecondaryStr, inline=False)
                
                embed.set_thumbnail(url=img)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed)
            except Exception as e:
                print(f'Error: {e}')
                await ctx.send(f'{user.mention}, I could not find the recommended runes for this champion.')    
        else:
            await ctx.send(f'{user.mention}, please specify a champion using **vrune [champion] | (role)**.')

def setup(client):
    client.add_cog(Champion(client))
