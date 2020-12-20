import discord, fileinput, sys, random
from discord.ext import commands

class Welcome(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('🗸 Welcome')
        
    def fileRead(self, ctx):
        with open(f'{ctx.guild.id}.txt', 'r') as guildFile:
            data = guildFile.readlines()
        return data
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if Welcome(self.client).checkForWChannel(member.guild):
            await self.client.get_channel(int(Welcome(self.client).welcomeChannel(member.guild))).send(f'{member.mention} welcome!')
            print(f'{member.name} joined {member.guild}')
        else:
            print(f'I saw that someone joined, but a welcome channel has not been set in {member.guild}')
                  
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setWelcomeChannel(self, ctx, newWChannel):
        if newWChannel.startswith("<#"):
            newWChannel = newWChannel[newWChannel.rfind('#')+1:newWChannel.rfind('>')]
        guildFile = open(f'{ctx.guild.id}.txt', 'r')
        data = guildFile.readlines()
        oldWChannel = 0
        for i in range(len(data)):
            if data[i].startswith("welcomeChannel="):
                oldWChannel = int(data[i][data[i].rfind('=')+1:])
                oldWChannel = str(oldWChannel)
        if oldWChannel == 0:
            await ctx.send(f'Welcome channel has been set to <#{newWChannel}>')
            guildFile.close()
            Welcome(self.client).setWelcomeChannelFile(ctx, oldWChannel, newWChannel)
        elif oldWChannel == newWChannel:
            await ctx.send(f'The welcome channel is already set to <#{newWChannel}>')
        elif oldWChannel != 0 and oldWChannel != newWChannel:
            await ctx.send(f'The welcome channel has been changed from <#{oldWChannel}> to <#{newWChannel}>')
            guildFile.close()
            Welcome(self.client).setWelcomeChannelFile(ctx, oldWChannel, newWChannel)
        else:
            await ctx.send('Something went wrong.')
        guildFile.close()
        
    @setWelcomeChannel.error
    async def setWelcomeChannel_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.client.get_channel(ctx.channel.id).send("You don't have permission to use this command.")
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeWelcomeChannel(self, ctx):
        if Welcome(self.client).checkForWChannel(ctx.guild):
            rmWelcomeChannel = f'welcomeChannel={str(Welcome(self.client).welcomeChannel(ctx.guild))}'
            for line in fileinput.input(f'{ctx.guild.id}.txt', inplace=1):
                if 'welcomeChannel=' in line:
                    line = line.replace(rmWelcomeChannel, ''.strip())
                sys.stdout.write(line)
            await self.client.get_channel(ctx.channel.id).send("The welcome channel has been removed.")
        else:
            await self.client.get_channel(ctx.channel.id).send("There is no welcome channel set.")

    @removeWelcomeChannel.error
    async def removeWelcomeChannel_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.client.get_channel(ctx.channel.id).send("You don't have permission to use this command.")

    def setWelcomeChannelFile(self, ctx, oldWChannel, newWChannel):
        if oldWChannel == 0:
            guildFile = open(f'{ctx.guild.id}.txt', 'a')
            guildFile.write(f'\nwelcomeChannel={newWChannel}')
            guildFile.close()
        else:
            for line in fileinput.input(f'{ctx.guild.id}.txt', inplace=1):
                if oldWChannel in line:
                    line = line.replace(oldWChannel, newWChannel.strip())
                sys.stdout.write(line)

    def welcomeChannel(self, guild):
        guildFile = open(f'{guild.id}.txt', 'r')
        data = guildFile.readlines()
        for i in range(len(data)):
            if data[i].startswith("welcomeChannel="):
                welcomeChannel = data[i][data[i].rfind('=')+1:]
        guildFile.close()
        return int(welcomeChannel)

    def checkForWChannel(self, guild):
        welcomeChannel = 0
        guildFile = open(f'{guild.id}.txt', 'r')
        data = guildFile.readlines()
        for i in range(len(data)):
            if data[i].startswith("welcomeChannel="):
                welcomeChannel = data[i][data[i].rfind('=')+1:data[i].rfind('\\')]
        guildFile.close()
        if welcomeChannel != 0:
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'{member.name} left {member.guild}')


def setup(client):
    client.add_cog(Welcome(client))