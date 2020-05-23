from discord.ext import commands
from database import db_exec, db_fetchall
from utils import programmes_util


class SetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setrank(self, ctx, rank_number: int, programme: str):
        user = ctx.message.author

        if rank_number <= 0 or rank_number >= 10000 or programme not in programmes_util.programmes:
            raise commands.UserInputError

        try:
            user_data_row = db_fetchall('SELECT user_id FROM user_data WHERE user_id = %s', (str(user.id),))

            if not user_data_row:
                db_exec('INSERT INTO user_data (user_id, username) VALUES (%s, %s)',
                        (str(user.id), user.name))

            db_exec('INSERT INTO ranks (user_id, rank, programme, offer_date) VALUES (%s, %s, %s, %s)',
                    (user.id, rank_number, programme,
                     '2020-04-15' if rank_number <= programmes_util.programmes[programme].places else None))
            await ctx.send(user.mention + ' Rank set.')
        except:
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
