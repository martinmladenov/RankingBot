from discord.ext import commands
# import datetime
import os
from database import *

bot = commands.Bot(command_prefix='.')


# @bot.event
# async def on_message(message):
#     content = message.content.lower()
#
#     if ('when' in content or 'where' in content) and ('rank' in content or 'result' in content or 'score' in content):
#         print(message.channel.name + ' | ' + message.author.name + ': ' + message.content)
#         print('sending!')
#
#         if message.author == bot.user:
#             return
#
#         now = datetime.datetime.now(tz=datetime.timezone.utc)
#
#         release = datetime.datetime(2020, 4, 14, hour=22, tzinfo=datetime.timezone.utc)
#
#         seconds = (release - now).total_seconds()
#
#         await message.channel.send(message.author.mention +
#                                    ' The ranking numbers for the Numerus clausus programmes will be released on '
#                                    '15 April at around **0:00 CEST** on Studielink!\n' +
#                                    f'Time remaining: **{int(seconds / 3600)} hours {int(seconds / 60 % 60)} '
#                                    f'minutes {int(seconds % 60)} seconds**')
#
#     await bot.process_commands(message)


@bot.command()
async def setrank(ctx, rank_number):
    user = ctx.message.author

    try:
        db_exec('insert into ranks (user_id, username, rank) values (%s, %s, %s)',
                (user.id, user.name, int(rank_number)))
        await ctx.send(user.mention + ' Rank set.')
    except:
        await ctx.send(user.mention + ' An error occurred while setting your rank.'
                                      ' If you have already set a rank, try clearing it using `.clearrank`')
        raise


@bot.command()
async def clearrank(ctx):
    user = ctx.message.author

    try:
        db_exec('delete from ranks where user_id = %s', (str(user.id),))
        await ctx.send(user.mention + ' Rank cleared.')
    except:
        await ctx.send(user.mention + ' An error occurred while clearing your rank.')
        raise


@bot.command()
async def ranks(ctx):
    rows = db_fetchall('select username, rank from ranks order by rank asc')

    all_ranks = '\n'.join(f'{x[1]} - {x[0]}' for x in rows)

    if not all_ranks:
        all_ranks = 'None'

    await ctx.send('**Top ranks:**\n'
                   '```'
                   + all_ranks +
                   '```'
                   'To set your rank, type `.setrank <rank>`')

    pass


bot.run(os.environ['DISCORD_SECRET'])
