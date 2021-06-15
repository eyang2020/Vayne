import os
import asyncio
import discord
import keep_alive
from datetime import datetime
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=['v'], intents=intents, help_command=None, case_insensitive=True)
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
COG_FOLDER = os.path.join(THIS_FOLDER, 'cogs')

cdDict = {
    'help': [],
    'lookup': [],
    'language': [],
    'skill': [],
    'rune': [],
    'sale': [],
    'wishlist': [],
    'wishadd': [],
    'wishremove': [],
    'rotation': []
}

champDict = {
    'Akali' : '<:Akali:853764762129924108>',
    'Aatrox' : '<:Aatrox:853764762192838687>',
    'Ahri' : '<:Ahri:853764762373324840>',
    'Alistar' : '<:Alistar:853764762721976360>',
    'Anivia' : '<:Anivia:853764762860912651>',
    'Amumu' : '<:Amumu:853764763074166794>',
    'Aphelios' : '<:Aphelios:853764763338407956>',
    'Annie' : '<:Annie:853764763393327124>',
    'Evelynn' : '<:Evelynn:853764769419755550>',
    'Ashe' : '<:Ashe:853764769480048661>',
    'Azir' : '<:Azir:853764769504165888>',
    'Braum' : '<:Braum:853764770281160724>',
    'Dr. Mundo' : '<:Dr:853764770300821524>',
    'Fiddlesticks' : '<:Fiddlesticks:853764770417868820>',
    'Graves' : '<:Graves:853764770473050132>',
    'Cassiopeia' : '<:Cassiopeia:853764770787622923>',
    'Aurelion Sol' : '<:Aurelion_Sol:853764771010838528>',
    'Caitlyn' : '<:Caitlyn:853764771023159338>',
    'Irelia' : '<:Irelia:853764771119628308>',
    'Gwen' : '<:Gwen:853764771156852778>',
    'Darius' : '<:Darius:853764771304046592>',
    'Blitzcrank' : '<:Blitzcrank:853764771366043669>',
    'Diana' : '<:Diana:853764771417292821>',
    'Camille' : '<:Camille:853764771451109416>',
    'Draven' : '<:Draven:853764771530932275>',
    'Corki' : '<:Corki:853764771732127765>',
    'Ivern' : '<:Ivern:853764771870408755>',
    'Ekko' : '<:Ekko:853764771903176715>',
    'Gangplank' : '<:Gangplank:853764771974217751>',
    'Illaoi' : '<:Illaoi:853764772045520916>',
    'Fizz' : '<:Fizz:853764772045783090>',
    'Brand' : '<:Brand:853764772055351346>',
    'Galio' : '<:Galio:853764772058365972>',
    'Elise' : '<:Elise:853764772138844160>',
    'Gragas' : '<:Gragas:853764772139237376>',
    'Cho\'Gath' : '<:Cho27Gath:853764772184981524>',
    'Jhin' : '<:Jhin:853764772218535996>',
    'Janna' : '<:Janna:853764772221550612>',
    'Bard' : '<:Bard:853764772222074920>',
    'Jarvan IV' : '<:Jarvan_IV:853764772272013322>',
    'Fiora' : '<:Fiora:853764772276994098>',
    'Jax' : '<:Jax:853764772285382676>',
    'Heimerdinger' : '<:Heimerdinger:853764772298489867>',
    'Jinx' : '<:Jinx:853764772330602546>',
    'Ezreal' : '<:Ezreal:853764772339122196>',
    'Jayce' : '<:Jayce:853764772352622602>',
    'Hecarim' : '<:Hecarim:853764772373069834>',
    'Garen' : '<:Garen:853764772398235658>',
    'Gnar' : '<:Gnar:853764772582785074>',
    'Kai\'Sa' : '<:Kai27Sa:853765147645182002>',
    'Kalista' : '<:Kalista:853765147674935306>',
    'Karma' : '<:Karma:853765148068806666>',
    'Karthus' : '<:Karthus:853765148078243900>',
    'Kassadin' : '<:Kassadin:853765148488630272>',
    'Katarina' : '<:Katarina:853765148673966141>',
    'Kayle' : '<:Kayle:853765148699525130>',
    'Kayn' : '<:Kayn:853765148909109289>',
    'Kennen' : '<:Kennen:853765149798039564>',
    'Kled' : '<:Kled:853765153460191242>',
    'Lillia' : '<:Lillia:853765154387001344>',
    'Morgana' : '<:Morgana:853765154398273536>',
    'Mordekaiser' : '<:Mordekaiser:853765154411249694>',
    'Lee Sin' : '<:Lee_Sin:853765154856632350>',
    'Nunu' : '<:Nunu:853765155073425428>',
    'Kha\'Zix' : '<:Kha27Zix:853765155182346300>',
    'Neeko' : '<:Neeko:853765155267543111>',
    'Ornn' : '<:Ornn:853765155278946314>',
    'Miss Fortune' : '<:Miss_Fortune:853765155455107072>',
    'Pyke' : '<:Pyke:853765155472932935>',
    'Qiyana' : '<:Qiyana:853765155666132992>',
    'Kindred' : '<:Kindred:853765155683041321>',
    'Pantheon' : '<:Pantheon:853765155774267393>',
    'Lissandra' : '<:Lissandra:853765156034838578>',
    'Kog\'Maw' : '<:Kog27Maw:853765156102078494>',
    'Rell' : '<:Rell:853765156202086430>',
    'LeBlanc' : '<:LeBlanc:853765156243636264>',
    'Lucian' : '<:Lucian:853765156273127444>',
    'Master Yi' : '<:Master_Yi:853765156311138305>',
    'Malzahar' : '<:Malzahar:853765156345610251>',
    'Malphite' : '<:Malphite:853765156433166336>',
    'Leona' : '<:Leona:853765156495163432>',
    'Lulu' : '<:Lulu:853765156555194368>',
    'Nocturne' : '<:Nocturne:853765156660314154>',
    'Renekton' : '<:Renekton:853765156718510141>',
    'Rengar' : '<:Rengar:853765156752064514>',
    'Orianna' : '<:Orianna:853765156782080031>',
    'Maokai' : '<:Maokai:853765156798070814>',
    'Nautilus' : '<:Nautilus:853765156834902017>',
    'Nidalee' : '<:Nidalee:853765156969775105>',
    'Lux' : '<:Lux:853765157012766720>',
    'Rek\'Sai' : '<:Rek27Sai:853765157066375168>',
    'Nami' : '<:Nami:853765157087477760>',
    'Quinn' : '<:Quinn:853765157100191774>',
    'Rammus' : '<:Rammus:853765157113298984>',
    'Nasus' : '<:Nasus:853765157154586715>',
    'Rakan' : '<:Rakan:853765157200724048>',
    'Olaf' : '<:Olaf:853765157205311509>',
    'Poppy' : '<:Poppy:853765157225103380>',
    'Riven' : '<:Riven:853765520977428501>',
    'Ryze' : '<:Ryze:853765521727160320>',
    'Sejuani' : '<:Sejuani:853765522021548052>',
    'Sett' : '<:Sett:853765522045927457>',
    'Samira' : '<:Samira:853765522062835712>',
    'Senna' : '<:Senna:853765522151178281>',
    'Seraphine' : '<:Seraphine:853765522155241494>',
    'Shaco' : '<:Shaco:853765522742313000>',
    'Rumble' : '<:Rumble:853765523433979905>',
    'Swain' : '<:Swain:853765526491627560>',
    'Sylas' : '<:Sylas:853765526836740106>',
    'Sion' : '<:Sion:853765527779147829>',
    'Shen' : '<:Shen:853765527893180437>',
    'Singed' : '<:Singed:853765528349835264>',
    'Viego' : '<:Viego:853765528434769992>',
    'Sivir' : '<:Sivir:853765528669388832>',
    'Urgot' : '<:Urgot:853765528677515264>',
    'Sona' : '<:Sona:853765528774639627>',
    'Skarner' : '<:Skarner:853765528937824316>',
    'Yone' : '<:Yone:853765528962072586>',
    'Shyvana' : '<:Shyvana:853765528975310869>',
    'Xin Zhao' : '<:Xin_Zhao:853765529096421386>',
    'Varus' : '<:Varus:853765529101664276>',
    'Volibear' : '<:Volibear:853765529368920065>',
    'Taliyah' : '<:Taliyah:853765529772359730>',
    'Syndra' : '<:Syndra:853765529831866409>',
    'Tahm Kench' : '<:Tahm_Kench:853765530086801408>',
    'Talon' : '<:Talon:853765530242908191>',
    'Taric' : '<:Taric:853765530258112563>',
    'Veigar' : '<:Veigar:853765530494042152>',
    'Vi' : '<:Vi:853765530494304257>',
    'Twitch' : '<:Twitch:853765530502561795>',
    'Tryndamere' : '<:Tryndamere:853765530532315187>',
    'Thresh' : '<:Thresh:853765530544766976>',
    'Xerath' : '<:Xerath:853765530573340702>',
    'Twisted Fate' : '<:Twisted_Fate:853765530590380042>',
    'Soraka' : '<:Soraka:853765530603618314>',
    'Teemo' : '<:Teemo:853765530653687818>',
    'Vladimir' : '<:Vladimir:853765530694713385>',
    'Xayah' : '<:Xayah:853765530762084352>',
    'Trundle' : '<:Trundle:853765530770210856>',
    'Tristana' : '<:Tristana:853765530791706634>',
    'Vel\'Koz' : '<:Vel27Koz:853765530791837716>',
    'Vayne' : '<:Vayne:853765530807697439>',
    'Udyr' : '<:Udyr:853765530829979658>',
    'Yasuo' : '<:Yasuo:853765530854752287>',
    'Wukong' : '<:Wukong:853765530867859507>',
    'Viktor' : '<:Viktor:853765530947551232>',
    'Warwick' : '<:Warwick:853765533013901342>',
    'Yuumi' : '<:Yuumi:853765898505814047>',
    'Zac' : '<:Zac:853765898708189216>',
    'Yorick' : '<:Yorick:853765898816585728>',
    'Zed' : '<:Zed:853765899449663488>',
    'Zilean' : '<:Zilean:853765899747852338>',
    'Ziggs' : '<:Ziggs:853765899785994240>',
    'Zoe' : '<:Zoe:853765899847991316>',
    'Zyra' : '<:Zyra:853765900175540244>'
}

runeDict = {
    # Branches
    'Sorcery' : '<:Rune_Sorcery:850205314887450624>',
    'Resolve' : '<:Rune_Resolve:850205314828468284>',
    'Precision' : '<:Rune_Precision:850205314506817560>',
    'Inspiration' : '<:Rune_Inspiration:850215452789571656>',
    'Domination' : '<:Rune_Domination:850205315173449760>',

    # Sorcery
    'Summon Aery' : '<:Rune_Summon_Aery:850512359642103838>',
    'Arcane Comet' : '<:Rune_Arcane_Comet:850512356784996423>',
    'Phase Rush' : '<:Rune_Phase_Rush:850512359403683890>',

    'Nullifying Orb' : '<:Rune_Nullifying_Orb:850512359185186888>',
    'Manaflow Band' : '<:Rune_Manaflow_Band:850512359331201114>',
    'Nimbus Cloak' : '<:Rune_Nimbus_Cloak:850512358995918878>',

    'Transcendence' : '<:Rune_Transcendence:850512359519682560>',
    'Celerity' : '<:Rune_Celerity:850512359339589703>',
    'Absolute Focus' : '<:Rune_Absolute_Focus:850512356588650506>',

    'Scorch' : '<:Rune_Scorch:850512359080722443>',
    'Waterwalking' : '<:Rune_Waterwalking:850512359571062784>',
    'Gathering Storm' : '<:Rune_Gathering_Storm:850512359062896671>',

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

    # Inspiration
    'Glacial Augment' : '<:Rune_Glacial_Augment:850514015783878686>',
    'Unsealed Spellbook' : '<:Rune_Unsealed_Spellbook:850514017796882462>',
    'Prototype: Omnistone' : '<:Rune_Prototype__Omnistone:850514017722171412>',

    'Hextech Flashtraption' : '<:Rune_Hextech_Flashtraption:850514432194379787>',
    'Magical Footwear' : '<:Rune_Magical_Footwear:850514017641431040>',
    'Perfect Timing' : '<:Rune_Perfect_Timing:850514432094240769>',

    'Future\'s Market' : '<:Rune_Future27s_Market:850514015309922335>',
    'Minion Dematerializer' : '<:Rune_Minion_Dematerializer:850514017591885825>',
    'Biscuit Delivery' : '<:Rune_Biscuit_Delivery:850514870637690911>',

    'Cosmic Insight' : '<:Rune_Cosmic_Insight:850514015667224639>',
    'Approach Velocity' : '<:Rune_Approach_Velocity:850514015481495592>',
    'Time Warp Tonic' : '<:Rune_Time_Warp_Tonic:850514017684553799>',

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
    '+9 Adaptive Force' : '<:Fragment_Adaptive_Force:850517181996859402>',
    '+10% Attack Speed' : '<:Fragment_Attack_Speed:850517181883219988>',
    '+8 Ability Haste' : '<:Fragment_Ability_Haste:850517181820436490>',
    '+6 Armor' : '<:Fragment_Armor:850517181392879667>',
    '+8 Magic Resist' : '<:Fragment_Magic_Resist:850517182014292019>',
    '+15-90 Health (based on level)' : '<:Fragment_Health:850517181837869107>'
}

# Commands
@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension=None):
    embed=discord.Embed(
        title='Cog Dashboard',
        color=discord.Colour(0x5500ff)
    )
    status = ''
    if extension is None:
        # reload all cogs
        client.dispatch('cog_unload_event')
        for fileName in os.listdir(COG_FOLDER):
            if fileName.endswith('.py'):
                extension = fileName[:-3]
                try:
                    client.unload_extension(f'cogs.{extension}')
                    client.load_extension(f'cogs.{extension}')
                    status += '✅`{}`\n'.format(extension)
                except:
                    status += '❌`{}`\n'.format(extension)
    else:
        # reload the specified cog
        try:
            if extension == 'champselect':
                client.dispatch('cog_unload_event')
            client.unload_extension(f'cogs.{extension}')
            client.load_extension(f'cogs.{extension}')
            status = '✅`{}`'.format(extension)
        except:
            status = '❌`{}`'.format(extension)
    # send report
    embed.add_field(name='\u2800', value=status, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

# cog init
for fileName in os.listdir(COG_FOLDER):
    if fileName.endswith('.py'):
        client.load_extension(f'cogs.{fileName[:-3]}')

# Events
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='vhelp'), status=discord.Status.online)
    print("Vayne is online.")

# Error Handling (Event)
@client.event
async def on_command_error(ctx, error):
    print(f'Error: {error}')
    # Cooldown Errors
    if isinstance(error, commands.CommandOnCooldown):
        user = ctx.message.author
        userId = user.id
        com = str(ctx.command).lower()
        if userId not in cdDict[com]:
            cdDict[com].append(userId)
            secondsLeft = round(error.retry_after)
            await ctx.send(f'{user.mention}, this command is on a `{secondsLeft} second` cooldown')
            await asyncio.sleep(secondsLeft)
            cdDict[com].remove(userId)

keep_alive.keep_alive()
client.run(TOKEN)
