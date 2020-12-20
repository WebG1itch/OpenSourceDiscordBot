import discord, fileinput, sys, random
from discord.ext import commands

class Roulette(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('🗸 Roulette')

    def fileRead(self, ctx):
        with open(f'{ctx.guild.id}.txt', 'r') as guildFile:
            data = guildFile.readlines()
        return data
        
    @commands.command(aliases=['rhelp'])
    async def rHelp(self, ctx): # When the user does /rHelp the bot will send a message explaining roulette. 
        embed=discord.Embed(title='Roulette Help',description='\'/claim\' to start\n\'/bet <coins> <any of the tags below>\' to bet\nExample: \'/bet 20 even\'\n\'/spin\' to play',color=0x008000)
        embed.add_field(name='red  |  1:1 payout',value='Bets on all red numbers.',inline=False)
        embed.add_field(name='black  |  1:1 payout',value='Bets on all black numbers.',inline=False)
        embed.add_field(name='green  |  35:1 payout',value='Bets on number 0',inline=False)
        embed.add_field(name='odd  |  1:1 payout',value='Bets on all odd numbers.',inline=False)
        embed.add_field(name='even  |  1:1 payout',value='Bets on all even numbers.',inline=False)
        embed.add_field(name='first12  |  2:1 payout',value='Bets on numbers 1-12',inline=False)
        embed.add_field(name='second12  |  2:1 payout',value='Bets on numbers 13-24',inline=False)
        embed.add_field(name='third12  |  2:1 payout',value='Bets on numbers 25-36.',inline=False)
        embed.add_field(name='col1  |  2:1 payout',value='Bets on the first column of numbers.',inline=False)
        embed.add_field(name='col2  |  2:1 payout',value='Bets on the second column of numbers.',inline=False)
        embed.add_field(name='col3  |  2:1 payout',value='Bets on the third column of numbers.',inline=False)
        embed.add_field(name='upper  |  1:1 payout',value='Bets on numbers 1-18',inline=False)
        embed.add_field(name='lower  |  1:1 payout',value='Bets on numbers 19-36',inline=False)
        embed.add_field(name='Any number 0-36 | 35:1 payout',value='Bets on the specific number chosen',inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/771757113134415875/785547677541990430/roulette-board.png")
        await self.client.get_channel(ctx.channel.id).send(embed=embed)
        
    @commands.command() # Simple command to check the amount of money a user has
    async def bank(self, ctx):
        await self.client.get_channel(ctx.channel.id).send(f'You have {Roulette(self.client).coinAmount(ctx)} coins in the bank.')

    @commands.command(aliases=['claim']) # The user needs coins. They can get coins by doing /claimCoins or /claim
    async def claimCoins(self, ctx):
        await self.client.get_channel(ctx.channel.id).send(Roulette(self.client).claimCoinsAction(ctx))

    @commands.command(aliases=['bet']) # When a user does /bet <coins> <place> the bot needs to store this bet in the server's txt file
    async def rouletteBet(self, ctx, betAmt, bet):
        alreadyBet = False
        data = Roulette(self.client).fileRead(ctx)
        for i in range(len(data)):
            if data[i].startswith(f'rbet{ctx.message.author.id}='):
                await self.client.get_channel(ctx.channel.id).send(f'You have already bet on this spin.')
                alreadyBet = True
        if alreadyBet == False:
            if Roulette(self.client).checkCoins(ctx) == False: # Next the bot needs to check to see if the user has any coins. If the user does not, the bot should give the user their coins
                await self.client.get_channel(ctx.channel.id).send('You haven\'t claimed your coins yet. Let me give you some to start you on your journey.')
                Roulette(self.client).claimCoins(ctx)
            await self.client.get_channel(ctx.channel.id).send(Roulette(self.client).betSequence(ctx, betAmt, bet))
        
    @commands.command() # 'spin' the wheel and tell the server the outcome
    async def spin(self, ctx):
        spinEmbed = Roulette(self.client).spinAction(ctx)
        await self.client.get_channel(ctx.channel.id).send(embed=spinEmbed)

    def betSequence(self, ctx, betAmt, bet):
        if int(Roulette(self.client).coinAmount(ctx)) >= int(betAmt): # The bot needs to check to see if the user has enough coins to place their bet
            guildFile = open(f'{ctx.guild.id}.txt', 'a')
            guildFile.write(f'rbet{ctx.message.author.id}={betAmt},{bet}\n')
            guildFile.close()
            return f'You bet {betAmt} coins on {bet}' # The bot confirms the user's bet
        elif int(Roulette(self.client).coinAmount(ctx)) < int(betAmt): # If the user does not have enough coins, the bot tells them
            return f'You have {Roulette(self.client).coinAmount(ctx)} coins. You cannot bet more than that.'

    def removeBets(self, ctx): # Needs to go through the server's file and remove all of the bets. This will be called after payouts and losses
        data = Roulette(self.client).fileRead(ctx)
        with open(f'{ctx.guild.id}.txt', 'w') as guildFile:
            for line in data:
                if line.startswith('rbet'):
                    guildFile.write(''.strip())
                else:
                    guildFile.write(line)
                
    def subtractBet(self, ctx, usrId, betAmt): # Needs to remove the appropriate amount of money from users that lost their bets
        rewrite = ''
        coins = 0
        data = Roulette(self.client).fileRead(ctx)
        for i in range(len(data)):
            if data[i].startswith(f'{usrId}-coins='):
                    rewrite = data[i]
                    coins = int(data[i][data[i].rfind('=')+1:len(data[i])].strip())
        with open(f'{ctx.guild.id}.txt', 'w') as guildFile: # Opens the file to write to it now.
            for line in data:
                if line == rewrite: # Check for user's id
                    guildFile.write(line.replace(str(coins), str(coins-int(betAmt)))) # Replaces the amount of coins the user had with their new total
                else:
                    guildFile.write(line) # rewrite the line's that aren't the user in question as if to skip the lines, and not delete them.
    
    def payout(self, ctx, member, betAmt, bet): # If the user won, call this. This should check to see how much the user bet and where. This will payout the appropriate amount based on that.
        if bet in ['green','0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36']:
            payout = betAmt * 35
        elif bet in ['red','black','even','odd','upper','lower']:
            payout = betAmt
        elif bet in ['first12','second12','third12','col1','col2','col3']:
            payout = betAmt * 2
        rewrite = '' 
        data = Roulette(self.client).fileRead(ctx)
        for i in range(len(data)):
            if data[i].startswith(f'{member}-coins='):
                    rewrite = data[i]
                    coins = int(data[i][data[i].rfind('=')+1:len(data[i])].strip())
        with open(f'{ctx.guild.id}.txt', 'w') as guildFile: # Opens the file to write to it now.
            for line in data:
                if line == rewrite: # Check for user's id
                    guildFile.write(line.replace(str(coins), str(coins+int(betAmt)))) # Replaces the amount of coins the user had with their new total
                else:
                    guildFile.write(line) # rewrite the line's that aren't the user in question as if to skip the lines, and not delete them.
        return f'{ctx.guild.get_member(int(member)).mention} won {payout} for betting on {bet}\n' # Tell user the good news

    def claimCoinsAction(self, ctx): # Claims coins for the user that requested. Give's them 50 coins
        if Roulette(self.client).checkCoins(ctx) == False: # Check if user has claimed coins yet
            guildFile = open(f'{ctx.guild.id}.txt', 'a')
            guildFile.write(f'{ctx.message.author.id}-coins=50\n')
            guildFile.close()
            return 'You now have 50 coins. Spend wisely!'
        else:
            return f'You have already claimed your coins. You have {Roulette(self.client).coinAmount(ctx)}.'

    def spinAction(self, ctx): # Random number gen from 0 - 36
        num = random.randint(0,36)
        spinEmbed=discord.Embed(title='The Results:',description=f'The ball landed on {num}',color=0x008000)
        winners = f''
        losers = f''          
        with open('rouletteNumbers.txt', 'r') as rouletteKey: # This file has all of the numbers of roulette and what bets they fall under
            line=rouletteKey.readlines()
            numProperties = line[num].split(',') # Separates all of the properties for the numbers into their own list items so that they can be compared to the actual outcome
        data = Roulette(self.client).fileRead(ctx)
        for i in range(len(data)): # Runs through all of the lines to find users' bets
            match = 0
            if data[i].startswith(f'rbet'): # Since I made all bets start with rbet, it's easy to find the bets
                usrId = data[i][data[i].rfind('rbet')+4:data[i].rfind('=')] # Gets the user's id number so their money can be changed
                betAmt = data[i][data[i].rfind('=')+1:data[i].rfind(',')].strip() # Get's the user's bet amount so their money can be changed with the right amount
                bet = data[i][data[i].rfind(',')+1:len(data[i])].strip() # get's where they bet to see if they won or lost
                for j in range(len(numProperties)): # Need to run through all of the properties of the specific number that the generator made
                    if bet == numProperties[j].strip(): # Checks for a match
                        match += 1
                if match == 0: # If no match, send the user's Id and bet amount so that their money can be adjusted 
                    Roulette(self.client).subtractBet(ctx,usrId,betAmt)
                    losers += f'{ctx.guild.get_member(int(usrId)).mention} lost {betAmt} for betting on {bet}.\n' # Tell user the bad news
                elif match > 0: # If there's a match, send their Id, bet amount and where they bet to payout()
                    winners += Roulette(self.client).payout(ctx, usrId, betAmt, bet) 
        if winners == '':
            spinEmbed.add_field(name='Winners',value='There were no winners.',inline=False)
        else:
            spinEmbed.add_field(name='Winners',value=winners,inline=False)
        if losers == '':
            spinEmbed.add_field(name='Losers',value='There were no losers.',inline=False)
        else: 
           spinEmbed.add_field(name='Losers',value=losers,inline=False)
        Roulette(self.client).removeBets(ctx) # remove all bets from the server file
        return spinEmbed
    
    def checkCoins(self, ctx): # Checks to see if the user has coins or not. Returns a boolean 
        data = Roulette(self.client).fileRead(ctx)
        for i in range(len(data)):
            if data[i].startswith(f'{ctx.message.author.id}-coins='):
                return True
        return False

    def coinAmount(self, ctx): # Checks and returns the number of coins that the user has
        data = Roulette(self.client).fileRead(ctx)
        coins = 0
        for i in range(len(data)):
            if data[i].startswith(f'{ctx.message.author.id}-coins='):
                coins = data[i][data[i].rfind('=')+1:len(data[i])].strip()
        return coins
        
def setup(client):
    client.add_cog(Roulette(client))