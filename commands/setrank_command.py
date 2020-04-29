from discord.ext import commands
from database import db_exec
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
            db_exec('INSERT INTO ranks (user_id, username, rank, programme, offer_date) VALUES (%s, %s, %s, %s, %s)',
                    (user.id, user.name, rank_number, programme,
                     '2020-04-15' if rank_number <= programmes_util.programmes[programme].places else None))
            await ctx.send(user.mention + ' Rank set.')
        except:
            await ctx.send(user.mention + ' Unable to set rank.'
                                          ' If you have already set a rank, try clearing it using '
                                          f'`.clearrank {programme}`')
            # raise

    @setrank.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(
                user.mention + f' Invalid arguments. Usage: `.setrank <rank> <{programmes_util.get_ids_string()}>`')
