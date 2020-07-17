import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from pathlib import Path
import random
import time
import os
import datetime
import json
import asyncio

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')
Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

marshDiscordId = 224618877626089483
jackDiscordId = 276462585690193921

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name=".help")
    await bot.change_presence(activity=activity)
    print(f'Logged on and ready to use!')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
            title="HomieBot Command List",
            description='Those are availble categories:',
            colour = discord.Colour.red()
        )
    embed.add_field(name='Fun', value="`.fun``", inline=True)
    embed.add_field(name='Info', value="``.info``", inline=True)
    await ctx.channel.send(embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(
            title="Information",
            description="Hello! I'm HomieBot. My parents are <@{}> and <@{}>. Hope you will enjoy my company.".format(str(marshDiscordId), str(jackDiscordId)),
            colour = discord.Colour.greyple()
        )
    await ctx.channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        pass

@bot.command(brief='In Progress 😊')
async def cd(ctx):
    Tday = datetime.date.today()
    f_date = datetime.date(2020, 8, 10)
    delta = f_date - Tday
    if ctx.author.id == marshDiscordId or ctx.author.id == 704589853974855770 or ctx.author.id == jackDiscordId:
        await ctx.channel.send(delta)

@bot.command(aliases=['8ball'], brief='AKA 8ball, Ask the bot a question that you dont want the answer to.')
async def eightball(ctx,*,question):
    responses = ['It is certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes - definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Reply hazy, try again.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                "Don't count on it.",
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good.',
                'Very doubtful.']
    await ctx.channel.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@bot.command(brief='Clears messages within the current channel.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx,amount):
    amount = int(amount)
    if amount <= 100:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.channel.send('Cannot delete more than 100 messages at a time!')

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.channel.send('Please put an amount to clear.')

@bot.command(aliases=['penis','pipa','pene'], brief='Ego problems? No problem I can help you with that.')
async def pp(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    no_use_pp = None
    PP_Size = random.randint(3,20)
    if member.id == 488959709609590787:
        member = no_use_pp
    if member.id == jackDiscordId:
        PP_Size = 20
    elif member.id == 464861706665984010:
        PP_Size = 1
    embed = discord.Embed(
        title = 'AYE DAWG NICE PEEPEE!',
        description = str(member.name) + '\'s penis size is ' + str(PP_Size) + 'cm 😘\n8' + ("=" * PP_Size) + 'D',
        colour = discord.Colour.magenta()
    )
    await ctx.channel.send(embed=embed)

@bot.command(aliases=['insult','burn'], brief='Insult someone until they cry')
async def roast(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    author = bot.user if member is ctx.author else ctx.author
    if bot.user.id == member.id:
        replys = ['Simmer down buddy 🔫',
                'You dare challenge thy master?! 💪',
                'OK homie relax.. 💩',
                'You aint even worth it dawg 🤏',
                'HA! Good one. 😂',
                'You done yet? Pussy.',
                'Fuck off!!'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')
    else:
        embed = discord.Embed(
            title = 'HOMIE INSULTS! 🔥',
            description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("insults.txt"),
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)
        file.close()

@bot.command(brief='Wanna hit on someone? Let me be your wingman!')
async def pickup(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    author = bot.user if member is ctx.author else ctx.author
    embed = discord.Embed(
        title = 'HOMIE PICKUPS! 🌈',
        description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("pickup.txt"),
        colour = discord.Colour.orange()
    )
    await ctx.channel.send(embed=embed)
    file.close()

async def lineChooser(filename):
    i = 0
    file = open(linksPath / filename,'rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(linksPath / filename,'rt')
    for line in file:
        i += 1
        if i == this_num:
            return str(line)

@bot.command(aliases=['duel'], brief='Fight someone on this server!')
@commands.max_concurrency(1,per=BucketType.default,wait=True)
async def fight(ctx, member : discord.Member):
    duel_authors_id = ctx.author.id
    duel_authors_name = ctx.author.name
    challenge_member_name = member.name
    challenge_member_id = member.id
    bot_id = bot.user.id

    hit_response = [    'cRaZyy',
                        'pOwerful',
                        'DEADLY',
                        'dangerous',
                        'deathly',
                        'l33t',
                        'amazing'
    ]
    
    #fighting yourself? Loser.
    if duel_authors_id == challenge_member_id:
        replys = [  'Dumbass.. You cant challenge yourself! 🤡',
                    'LOL! IDIOT! 🤣',
                    'Homie... Chillax. Stop beefing with yo self 👊',
                    'You good bro? 😥',
                    'REEEEELLLAAAAXXXXXXXXX 😬',
                    'Its gonna be okay 😔'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')

    #fighting the bot? KEKW
    elif challenge_member_id == bot_id:
        replys = [  'Simmer down buddy 🔫',
                    'You dare challenge thy master?! 💪',
                    'OK homie relax.. 💩',
                    'You aint even worth it dawg 🤏',
                    'You a one pump chump anyway 🤡',
                    'HA! Good one. 😂',
                    'You done yet? Pussy.'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')

    #fighting other users
    else:
        embed = discord.Embed(
            title = '⚔️ ' + duel_authors_name + ' has challenged ' + challenge_member_name + ' to a fight!',
            description=member.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!',
            colour = discord.Colour.red()
        )
        await ctx.channel.send(embed=embed)
        
        fight_turn = 0
        challenge_member_health = int(100)
        duelers_health = int(100)
        punch_damage = int(random.randint(1,100))
        def inner_check(message):
            return message.content == 'punch' or message.content == 'defend' or message.content == 'end'

        while challenge_member_health > 0 or duelers_health > 0:
            try:
                msg = await bot.wait_for('message', check=inner_check, timeout=30.0)
            except asyncio.TimeoutError:
                if (fight_turn % 2) == 0:
                    await ctx.channel.send('Nice fight idiots.. **' + duel_authors_name + '** wins!')
                    break
                else:
                    await ctx.channel.send('Nice fight idiots.. **' + challenge_member_name + '** wins!')
                    break
            if str(msg.content) == 'punch' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                fight_turn += 1

                #jack always punches for 100 damage cuz he is 4WeirdBuff
                if msg.author.id == jackDiscordId or msg.author.id == marshDiscordId:
                    punch_damage = 100
                duelers_health -= punch_damage
                await ctx.channel.send('**' + challenge_member_name + '** lands a ' + f'{random.choice(hit_response)}' + ' hit on **' + duel_authors_name + '** dealing `' + f'{punch_damage}' + '` damage!\n**' + duel_authors_name + '** is left with `' + f'{duelers_health}' + '` health!')
                                
                if duelers_health <= 0:
                    embed = discord.Embed(
                        title = 'STOP! STOP! STOP! THE FIGHT IS OVER!!!',
                        description = '**' + f'{challenge_member_name}' + '** wins with just `' + f'{challenge_member_health}' + ' HP` left!',
                        colour = discord.Colour.teal()
                    )
                    await ctx.channel.send(embed=embed)
                    break
                else:
                    await ctx.channel.send(ctx.author.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')
                    punch_damage = int(random.randint(1,int(f'{challenge_member_health}'))) 
              
            elif str(msg.content) == 'punch' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                fight_turn += 1

                #jack always punches for 100 damage cuz he is 4WeirdBuff
                if msg.author.id == jackDiscordId or msg.author.id == marshDiscordId:
                    punch_damage = 100
                challenge_member_health -= punch_damage
                await ctx.channel.send('**' + duel_authors_name + '** lands a ' + f'{random.choice(hit_response)}' + ' hit on **' + challenge_member_name + '** dealing `' + f'{punch_damage}' + '` damage!\n**' + challenge_member_name + '** is left with `' + f'{challenge_member_health}' + '` health!')
                           
                if challenge_member_health == 0:
                    embed = discord.Embed(
                        title = 'STOP! STOP! STOP! THE FIGHT IS OVER!!!',
                        description = '**' + f'{duel_authors_name}' + '** wins with just `' + f'{duelers_health}' + ' HP` left!',
                        colour = discord.Colour.teal()
                    )
                    await ctx.channel.send(embed=embed)
                    break
                else:
                    await ctx.channel.send(member.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')
                    punch_damage = int(random.randint(1,int(f'{duelers_health}')))  

            elif str(msg.content) == 'defend' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                fight_turn += 1
                await defenseResponse(ctx, duel_authors_name, member.mention)
            elif str(msg.content) == 'defend' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                fight_turn += 1
                await defenseResponse(ctx, challenge_member_name, ctx.author.mention)
            elif str(msg.content) == 'end' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                await ctx.channel.send(duel_authors_name + ' has ended the fight. What a wimp.')
                break
            elif str(msg.content) == 'end' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                await ctx.channel.send(challenge_member_name + ' has ended the fight. What a wimp.')
                break   

async def defenseResponse(ctx, person, mentionedUser):
    defence_points = int(random.randint(1,10))
    await ctx.channel.send('**' + f'{person}' + '** boosted their defense by `' + f'{defence_points}' + '` points!')
    await ctx.channel.send(mentionedUser + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

@fight.error
async def fight_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send('Who you tryna fight, the air?! Choose someone to fight you pleb! 🤡')

@bot.command(brief='Enlarge and view your profile picture or another member')
async def av(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    embed = discord.Embed(
        title = str(member.name),
        description = 'Avatar',
        colour = discord.Colour.light_grey()
    )
    embed.set_image(url=member.avatar_url)
    await ctx.channel.send(embed=embed)

startup_extensions = ["gif","music"]

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

file = open(Discord_Bot_Dir / 'token.txt','rt')
bot.run(str(file.read()))