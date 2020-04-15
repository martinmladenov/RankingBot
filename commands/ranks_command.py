from discord.ext import commands
from database import db_fetchall


class RanksCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ranks(self, ctx):
        rows = db_fetchall('select username, rank from ranks order by rank asc')

        all_ranks = '\n'.join(f'{x[1]} - {x[0]}' for x in rows)

        if not all_ranks:
            all_ranks = 'None'

        await ctx.send('**Top ranks:**\n'
                       '```'
                       + all_ranks +
                       '```'
                       'To set your rank, type `.setrank <rank>`')
