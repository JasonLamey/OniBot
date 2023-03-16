import os
import random
import discord
import requests
import json
import re
from dotenv import load_dotenv

from discord.ext import commands


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

# host = 'https://www.side7.com'  # TODO switch the hosts before pushing to production
host = 'http://lameyhouse2.ddns.net:3000'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents,
                   description='!help')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user.name} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})'
          )


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}! Welcome to Side 7!')


@bot.command(name='featured_artist', help='Tells you the Featured Artist of the Day')
async def featured_artist(ctx):
    print('Request for FAotD received.')

    s7response = requests.get(host + "/oni/faotd")

    response = ''
    if s7response.status_code == 200:
        print("FAotD - Good status")
        data = s7response.json()
        user = dict(data[0])
        full_name = ''
        if user['full_name'] != '':
            full_name = f"{user['full_name']} ({user['username']})"
        else:
            full_name = user['username']

        response = f"Today's Featured Artist is: {full_name}! Check their art out at https://www.side7.com/u/{user['username']}/gallery"
    elif s7response.status_code == 404:
        print("No FAotD - Missing")
        response = "I'm sorry, but there doesn't seem to be a Featured Artist today."
    else:
        print(f'The returned status code is {s7response.status_code}')
        response = "I'm sorry. I'm having trouble communicating with Side 7 right now. Try again later."

    await ctx.send(response)


@bot.command(name='random_art', help='Links to a random piece of art by the specified artist')
async def random_art(ctx, username=None):
    print(f'Request for random art received for user {username}.')
    if username is None:
        username = ''

    s7response = requests.get(host + "/oni/random/" + username)

    response = ''
    if s7response.status_code == 200:
        print("Random Art - Good status")
        data = s7response.json()
        # print(data)
        file = dict(data[0])
        filehash = file["file_hash"]
        title = file["title"]
        rating = file["rating"]
        qualifiers = file["qualifiers"]
        content_type = file["content_type"]
        artist = file["username"]
        if qualifiers != 'None':
            qualifiers = f' ({qualifiers})'
        else:
            qualifiers = ''

        response = f"Check this {content_type} by {artist} out: {title} - Rated: {rating}{qualifiers} {host}/content/{filehash}"
    elif s7response.status_code == 404:
        print("No Random Art - User not found or has no artwork.")
        response = f"I'm sorry, but either {username} doesn't exist, or they have no artwork to share."
    elif s7response.status_code == 403:
        print("No Random Art - Artist is not Active")
        response = f"I'm sorry, but I am not allowed to share art from that artist."
    else:
        print(f'The returned status code is {s7response.status_code}')
        response = "I'm sorry. I'm having trouble communicating with Side 7 right now. Try again later."

    await ctx.send(response)


@bot.command(name='tag_art', help='Links to a random piece of art with the specified tag')
async def tag_art(ctx, tag=''):
    print(f'Request for random art by tag received for tag {tag}.')
    if not tag:
        await ctx.send(f'Um, what tag do you want me to search for? (Use `!tag_art <tag>`)')
    else:
        s7response = requests.get(host + "/oni/by_tag/" + tag)

        response = ''
        if s7response.status_code == 200:
            print("Random Art - Good status")
            data = s7response.json()
            # print(data)
            file = dict(data[0])
            filehash = file["file_hash"]
            title = file["title"]
            rating = file["rating"]
            qualifiers = file["qualifiers"]
            content_type = file["content_type"]
            artist = file["username"]
            if qualifiers != 'None':
                qualifiers = f' ({qualifiers})'
            else:
                qualifiers = ''

            response = f"Check this {content_type} by {artist} out: {title} - Rated: {rating}{qualifiers} {host}/content/{filehash}"
        elif s7response.status_code == 404:
            print("No Random Art by Tag - Tag returned no artwork.")
            response = f"I'm sorry, but it seems there is no art with the tag '{tag}'."
        else:
            print(f'The returned status code is {s7response.status_code}')
            response = "I'm sorry. I'm having trouble communicating with Side 7 right now. Try again later."

        await ctx.send(response)


@bot.command(name='portrait', help='See what I look like')
async def portrait(ctx):
    image_hashes = [
        'R19ob2RDr2',
        'z39qYoo39R',
        'eXrBZOnQrR',
        'eXrBZOOerR'
    ]

    image_hash = random.choice(image_hashes)

    await ctx.send(f"Here's a picture of me! {host}/content/{image_hash}")


# @bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
# async def nine_nine(ctx):
#     brooklyn_99_quotes = [
#         'I\'m the human form of the 💯 emoji.',
#         'Bingpot!',
#         (
#             'Cool. Cool cool cool cool cool cool cool, '
#             'no doubt no doubt no doubt no doubt.'
#         ),
#     ]
#
#     response = random.choice(brooklyn_99_quotes)
#     await ctx.send(response)


@bot.command(name="roll_dice", help='Simulates rolling dice. !roll_dice <dice_notation> (e.g. 3d6).')
# async def roll(ctx, number_of_dice: int, number_of_sides: int):
async def roll(ctx, dice_to_roll):
    number_of_dice, number_of_sides = dice_to_roll.split('d')
    dice = [
        str(random.choice(range(1, int(number_of_sides) + 1)))
        for _ in range(int(number_of_dice))
    ]
    total = 0
    for i in dice:
        total += int(i)

    rolls = ', '.join(dice)
    await ctx.send(f'Rolls: {rolls} - Total: {total}')


# @bot.command(name='create_channel', help='Creates a new text channel. !create_channel <channel_name> (Admin only)')
# @commands.has_role('Admins')
# async def create_channel(ctx, channel_name='Side7'):
#     guild = ctx.guild
#     existing_channel = discord.utils.get(guild.channels, name=channel_name)
#     if not existing_channel:
#         print(f'Creating new channel: {channel_name}')
#         await guild.create_text_channel(channel_name)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    oni_responses = [
        'I\'m Oni!',
        'Mew!',
        'Purr purr purr',
        'That\'s me!'
    ]

    if findWholeWord('oni')(message.content) is not None:
        response = random.choice(oni_responses)
        await message.channel.send(response)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


bot.run(TOKEN)
