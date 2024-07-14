import subprocess
import json
import os
from datetime import datetime
import asyncio
import discord
import pytz
from discord import Message, Guild, TextChannel, Permissions
from discord.ext import commands

intents = discord.Intents.default()  # This is how you define 'intents'
bot = commands.Bot(command_prefix='g!', intents=intents)

if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)

async def UpdateMemberCount():
    while True:
        usercount = len(list(filter(lambda m: m.bot == False, bot.users)))
        await bot.change_presence(activity=discord.Game(f'🌎 | auf {len(bot.guilds)} Server'))
        await asyncio.sleep(50)

@bot.event
async def on_ready():
    print(f'{bot.user} ist nun online!')
    print(f'{bot.user.id}')
    await bot.loop.create_task(UpdateMemberCount())


@bot.command()
async def addGlobal(ctx):
    if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
            server = {
                "guildid": ctx.guild.id,
                "channelid": ctx.channel.id,
                "invite": f'{(await ctx.channel.create_invite()).url}'
            }
            servers["servers"].append(server)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Willkommen im GlobalChat von Encoders Community**",
                                  description="Dein Server ist einsatzbereit!"
                                              " Ab jetzt werden alle Nachrichten in diesem Channel direkt an alle"
                                              " anderen Server weitergeleitet!",
                                  color=0x2ecc71)
            embed.set_footer(text='Bitte beachte, dass im GlobalChat stets ein Slowmode von mindestens 5 Sekunden'
                                  ' gesetzt sein sollte.')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Du hast bereits einen GlobalChat auf deinem Server.\r\n"
                                              "Bitte beachte, dass jeder Server nur einen GlobalChat besitzen kann.",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)
            await ctx.channel.edit(slowmode_delay=5, topic="""
**<a:welt:831123015517208597> | Encoders Community Global Chat


────────────────────────────
🔗 | Server Invite: https://discord.gg/KSEykyR4Qm



────────────────────────────
🤖 | Den Bot Invitest du mit dem Befehl __g!invite__! Wir freuen uns über jeden neuen Global Chat <3! Mit dem Befehl __g!addGlobal__ fügst du den global Chat dann in den individuellen Chat auf deinem Server hinzu!



────────────────────────────
<a:Alarm:827807392589676564> | Bitte halte dich an alle Regeln in <#810900008219705384>! Wenn du Support benötigst dann schreibe <@835602492862890024> an oder melde dich bei    https://discord.gg/KSEykyR4Qm**""")


@bot.command()
async def removeGlobal(ctx):
    if ctx.member.guild_permissions.administrator:
        if guild_exists(ctx.guild.id):
            globalid = get_globalChat_id(ctx.guild.id)
            if globalid != -1:
                servers["servers"].pop(globalid)
                with open('servers.json', 'w') as f:
                    json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Auf Wiedersehen!**",
                                  description="Der GlobalChat wurde entfernt. Du kannst ihn jederzeit mit"
                                              " `g!addGlobal` neu hinzufügen",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="Du hast noch keinen GlobalChat auf deinem Server.\r\n"
                                              "Füge einen mit `g!addGlobal` in einem frischen Channel hinzu.",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)


#########################################

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.content.startswith('!'):
        if get_globalChat(message.guild.id, message.channel.id):
            await sendAll(message)
    await bot.process_commands(message)


#########################################

async def sendAll(message: Message):
    conent = message.content
    author = message.author
    attachments = message.attachments
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(description=conent, timestamp=datetime.now().astimezone(tz=de), color=author.color)

    icon = author.avatar_url
    embed.set_author(name=author.name, icon_url=icon)

    icon_url = "https://images-ext-1.discordapp.net/external/UhuF1jw07zSR1onvtJ3vs1xxctys7s5gsFTjUdPdmcM/%3Fsize%3D1024/https/cdn.discordapp.com/icons/793403717859803156/1f7ed4541dfbafe1f3d4f3a11aa5c454.webp?width=178&height=178"
    icon = message.guild.icon_url
    if icon:
        icon_url = icon
    embed.set_thumbnail(url=icon_url)
    embed.set_footer(
        text=f'{message.guild.name} | Server User: {message.guild.member_count}',
        icon_url=f'{message.guild.icon_url}')
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.add_field(name="** **", value="`📌`[Support](https://discord.gg/8DSvY9mmQy)・`🤖`[Bot-Invite](https://discord.com/api/oauth2/authorize?client_id=922536268892622888&permissions=8&scope=bot%20applications.commands)", inline=False)
    


    if len(attachments) > 0:
        img = attachments[0]
        embed.set_image(url=img.url)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms: Permissions = channel.permissions_for(guild.get_member(bot.user.id))
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=embed)
                    else:
                        await channel.send('{0}: {1}'.format(author.name, conent))
                        await channel.send('Es fehlen einige Berechtigungen. '
                                           '`Nachrichten senden` `Links einbetten` `Datein anhängen`'
                                           '`Externe Emojis verwenden`')
    await message.delete()
async def sendAllWillkommen(ctx):
    embed = discord.Embed(
        title=f"Willkommen!",
        description=f'Der Server {ctx.guild.name} hat den Bot nun hinzugefügt!',
        color=0x662a85,
        timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f'{ctx.guild.name} | {ctx.guild.member_count} User',
                     icon_url=f'{ctx.guild.icon_url}')
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name=f'⠀', value='⠀', inline=False)
    embed.add_field(
        name=f'Support & Bot⠀',
        value=
        f'[Support & modmail](https://discord.gg/8DSvY9mmQy)・[Bot invite]()',
        inline=False)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                await channel.send(embed=embed)
    await ctx.message.delete()


def guild_exists(guildid):
    for server in servers['servers']:
        if int(server['guildid'] == int(guildid)):
            return True
    return False


def get_globalChat(guild_id, channelid=None):
    globalChat = None
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    globalChat = server
            else:
                globalChat = server
    return globalChat


def get_globalChat_id(guild_id):
    globalChat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            globalChat = i
        i += 1
    return globalChat

class NewHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.context
        embed = discord.Embed(
            title="**Encoders Community**",
            description="**Prefix: g! | Commands:**",
            color=discord.Color.blue()
        )
        embed.add_field(name='addGlobal', value='Fügt den Global Chat in den Channel hinzu', inline=False)
        embed.add_field(name='removeGlobal', value='Entfernt den Global Chat', inline=False)
        embed.add_field(name='invite', value='Kannst den Global Chat Inviten', inline=False)
        embed.add_field(name='support', value='Zeige den Support Server an', inline=False)
        await destination.send(embed=embed)
bot.help_command = NewHelpCommand()

@bot.event
async def on_guild_join(guild):
    print(f'Bot auf Server {guild.name} hinzugefügt!')
    channel = bot.get_channel(1261995769750360105)
    if channel:
        embed = discord.Embed(
            title='Bot auf Server hinzugefügt!',
            description=
            f'Server Name: {guild.name}\nServer ID: {guild.id}\nAnzahl an Mitgliedern: {guild.member_count}\n\n**Neue Anzahl an Servern: {len(bot.guilds)}**'
        )
        embed.set_thumbnail(url=f'{guild.icon_url}')
        await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    print(f'Bot auf Server {guild.name} entfernt!')
    channel = bot.get_channel(1261995769750360105)
    if channel:
        embed = discord.Embed(
            title='Bot auf Server entfernt!',
            description=
            f'Server Name: {guild.name}\nServer ID: {guild.id}\nAnzahl an Mitgliedern: {guild.member_count}\n\n**Neue Anzahl an Servern: {len(bot.guilds)}**'
        )
        embed.set_thumbnail(url=f'{guild.icon_url}')
        await channel.send(embed=embed)

@bot.command()
async def invite(ctx):
    embed=discord.Embed(title="\nInvite<a:Blob_Join:858565965854670878>\n", url="",color=0x662a85)
    await ctx.send(embed=embed)

@bot.command(name='support', aliases=['ss'])
async def support(ctx):
		
		embed = discord.Embed(
				title = f'Link <:Clyde_Bot:868384930147749910>',
				description = '**[Support server](https://discord.gg/encoders)**',
				color=0x662a85)
		await ctx.send(embed=embed)

@bot.command()
async def rs(ctx):
    await ctx.send("Restarting...")
    os.startfile(__file__)
    os._exit(1)

subprocess.Popen(["python3", "app.py"])

bot.run(os.environ.get('TOKEN'))