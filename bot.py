import discord, os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '/',intents=intents)

def read_token():
    with open("token.txt","r") as f:
        lines = f.readlines()
        return lines[0].strip()
    
@client.event
async def on_ready():
    print("I'm ready!")
    await client.change_presence(activity=discord.Game(name="Version 0.0.4"))
    
@client.event
async def on_guild_join(guild):
    print(f'I joined a new guild: \'{guild}\' #{guild.id}')
    guildFile = open(f'{guild.id}.txt','x')
    guildFile.close()
    print(f'File \'{guild.id}.txt\' created for \'{guild}\'')  

@client.command()
async def say(ctx, *, statement):
    await ctx.send(f'{statement}')
    
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)} ms')
    
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    print(f'Loaded {extension}')
    
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    print(f'Unloaded {extension}')
    
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f'Reloaded {extension}')
    
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        
client.run(read_token())