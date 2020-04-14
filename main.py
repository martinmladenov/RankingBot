from discord.ext import commands
import datetime
import os

bot = commands.Bot(command_prefix='.')


@bot.event
async def on_message(message):
    content = message.content.lower()

    if ('when' in content or 'where' in content) and ('rank' in content or 'result' in content or 'score' in content):
        print(message.channel.name + ' | ' + message.author.name + ': ' + message.content)
        print('sending!')

        if message.author == bot.user:
            return

        now = datetime.datetime.now(tz=datetime.timezone.utc)

        release = datetime.datetime(2020, 4, 14, hour=22, tzinfo=datetime.timezone.utc)

        seconds = (release - now).total_seconds()

        await message.channel.send(message.author.mention +
                                   ' The ranking numbers for the Numerus clausus programmes will be released on '
                                   '15 April at around **0:00 CEST** on Studielink!\n' +
                                   f'Time remaining: **{int(seconds / 3600)} hours {int(seconds / 60 % 60)} '
                                   f'minutes {int(seconds % 60)} seconds**')

    await bot.process_commands(message)

bot.run(os.environ['DISCORD_SECRET'])
