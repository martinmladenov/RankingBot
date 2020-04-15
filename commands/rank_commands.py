from discord.ext import commands
from database import db_exec, db_fetchall


class RankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setrank(self, ctx, rank_number):
        user = ctx.message.author

        try:
            db_exec('insert into ranks (user_id, username, rank) values (%s, %s, %s)',
                    (user.id, user.name, int(rank_number)))
            await ctx.send(user.mention + ' Rank set.')
        except:
            await ctx.send(user.mention + ' An error occurred while setting your rank.'
                                          ' If you have already set a rank, try clearing it using `.clearrank`')
            raise

    @commands.command()
    async def clearrank(self, ctx):
        user = ctx.message.author

        try:
            db_exec('delete from ranks where user_id = %s', (str(user.id),))
            await ctx.send(user.mention + ' Rank cleared.')
        except:
            await ctx.send(user.mention + ' An error occurred while clearing your rank.')
            raise

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

        pass
