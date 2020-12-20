import discord, fileinput, sys, random
from discord.ext import commands

class Shop(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('🗸 Shop (incomplete)')

    def fileRead(self, ctx):
        with open(f'{ctx.guild.id}.txt', 'r') as guildFile:
            data = guildFile.readlines()
        return data
    
def setup(client):
    client.add_cog(Shop(client))
    
