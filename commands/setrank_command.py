from discord.ext import commands
from utils import programmes_util
from datetime import date


class SetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setrank(self, ctx, rank_number: int, programme: str):
        user = ctx.message.author

        if rank_number <= 0 or rank_number >= 10000 or programme not in programmes_util.programmes:
            raise commands.UserInputError

        try:
            user_data_row = await self.bot.db_conn.fetchrow('SELECT user_id FROM user_data WHERE user_id = $1',
                                                            str(user.id))

            if not user_data_row:
                await self.bot.db_conn.execute('INSERT INTO user_data (user_id, username) VALUES ($1, $2)',
                                               str(user.id), user.name)

            await self.bot.db_conn.execute(
                'INSERT INTO ranks (user_id, rank, programme, offer_date) VALUES ($1, $2, $3, $4)',
                str(user.id), rank_number, programme,
                date(2020, 4, 15) if rank_number <= programmes_util.programmes[programme].places else None)
            await ctx.send(user.mention + ' Rank set.')
        except Exception:
            await ctx.send(user.mention + ' Unable to set rank.'
                                          ' If you have already set a rank, try clearing it using '
                                          f'`.clearrank {programme}`')
            # raise

    @setrank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(
                user.mention + f' Invalid arguments. Usage: `.setrank <rank> <{programmes_util.get_ids_string()}>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(SetrankCommand(bot))
