from discord.ext import commands
from utils import programmes_util, offer_date_util
from services import ranks_service
from services.errors.date_incorrect_error import DateIncorrectError


class AddmanualdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addmanualdate(self, ctx, programme: str, rank_number: int, day: str, month: str):
        user = ctx.message.author

        if not ctx.guild:
            await ctx.send(user.mention + ' You don\'t have permission to execute this command')
            return

        offer_date = offer_date_util.parse_offer_date(day, month)

        async with self.bot.db_conn.acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            tr = connection.transaction()
            await tr.start()

            try:
                await ranks.add_rank(rank_number, programme, offer_date=offer_date)

                if rank_number <= programmes_util.programmes[programme].places:
                    raise DateIncorrectError

                await tr.commit()
                await ctx.send(user.mention + ' Rank and offer date added.')

            except DateIncorrectError:
                await tr.rollback()
                await ctx.send(user.mention + ' There\'s no need to set this offer date as this rank is '
                                              'within the programme limit.')
            except:
                await tr.rollback()
                raise

    @addmanualdate.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError) \
                or isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            await ctx.send(
                user.mention + f' Invalid arguments. Usage: `.addmanualdate <{programmes_util.get_ids_string()}> '
                               '<rank> <day> <month>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(AddmanualdateCommand(bot))
