from discord.ext import commands
from database import db_fetchall


class RanksCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ranks(self, ctx):
        rows = db_fetchall('SELECT username, rank, programme FROM ranks ORDER BY rank ASC')

        curr_programmes = set(map(lambda x: x[2], rows))
        grouped_ranks = [(p, [row for row in rows if row[2] == p]) for p in curr_programmes]

        all_ranks = ''.join(
            (f'_{group[0]}:_ ```' + '\n'.join(
                ((' ' * (4 - len(str(x[1])))) + str(x[1]) + '  ' + x[0]) for x in group[1]) + '```\n' for group in
             grouped_ranks))

        if not all_ranks:
            all_ranks = '_None_\n\n'

        await ctx.send('**Top ranks:**\n\n'
                       + all_ranks +
                       '_Please note: This bot is purely for fun, the ranking numbers do not'
                       ' represent performance at university_\n'
                       'To set your rank, type `.setrank <rank>`')

    @ranks.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.ranks`')
