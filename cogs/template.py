import discord, fileinput, sys, random
from discord.ext import commands

class Template(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('🗸 Template')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)} ms')

    def fileRead(self, ctx):
        with open(f'{ctx.guild.id}.txt', 'r') as guildFile:
            data = guildFile.readlines()
        return data
    
def setup(client):
    client.add_cog(Template(client))