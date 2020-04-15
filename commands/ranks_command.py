from discord.ext import commands
from database import db_fetchall


class RanksCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ranks(self, ctx):
        rows = db_fetchall('SELECT username, rank FROM ranks ORDER BY rank ASC')

        all_ranks = '\n'.join(f'{x[1]} - {x[0]}' for x in rows)

        if not all_ranks:
            all_ranks = 'None'

        await ctx.send('**Top ranks:**\n'
                       '```'
                       + all_ranks +
                       '```'
                       '_Please note: This bot is purely for fun, the ranking numbers do not'
                       ' represent performance at university_\n'
                       'To set your rank, type `.setrank <rank>`')

    @ranks.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.ranks`')
