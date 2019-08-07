import discord
import MCRcon.mcrcon
import socket
import json

with open('config.json') as file:
    config = json.load(file)

bot = discord.Client()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config['rcon']['IP'], config['rcon']['port']))
mcrcon.login(sock, config['rcon']['password'])

def toMinecraft(message):
    command = """tellraw @a ["",{"text":"["},{"text":"%s","color":"dark_aqua"},{"text":" | "},{"text":"#%s","color":"dark_aqua"},{"text":"] %s"}]""" % (message.author.display_name, message.channel.name, message.content)
    mcrcon.command(sock, command)

def parseLogLine(line):
    parts = []
    start = 0
    for i in range(2):
        lIndex = line.find('[', start)
        start = lIndex + 1
        rIndex = line.find(']', start)
        start = rIndex + 1
        parts.append(line[lIndex + 1:rIndex])
    parts.append(line[start + 2:].replace('\n', ''))
    return parts

def parseChatMessage(messageType, content):
    if messageType != "Server thread/INFO":
        return False
    lNick = content.find('<')
    if lNick == -1:
        return False
    rNick = content.find('>')
    nick = content[lNick + 1:rNick]
    message = content[rNick + 2:]
    return nick, message

@bot.event
async def on_ready():
    print(f'MineCord logged in as {bot.user}.')
    lastMessage = None
    while True:
        with open(config['minecraftLog']) as logfile:
            lastLine = list(logfile)[-1]
            if lastMessage != lastLine:
                lastMessage = lastLine
                time, messageType, content = parseLogLine(lastLine)
                print(f"{time}-{messageType}-{content}")
                if parseChatMessage(messageType, content):
                    nick, message = parseChatMessage(messageType, content)
                    await bot.get_channel(config["minecraftToDiscordChannel"]).send(f"<{nick}> {message}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id in config["discordToMinecraftChannels"]:
        toMinecraft(message)

bot.run(config["key"])
sock.close()