from discord.ext import commands
from utils.offer_date_util import parse_offer_date
from helpers import programmes_helper
from services import ranks_service
from services.errors.entry_not_found_error import EntryNotFoundError
from services.errors.date_incorrect_error import DateIncorrectError
import constants


class SetofferdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setofferdate(self, ctx, day: str, month: str, programme: str, year: int = None):
        if year is None:
            year = constants.current_year

        user = ctx.message.author

        offer_date = parse_offer_date(day, month)

        async with self.bot.db_conn.acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            try:
                await ranks.set_offer_date(str(user.id), programme, offer_date, year)
            except EntryNotFoundError:
                await ctx.send(user.mention + ' Before setting an offer date, please set your rank first using '
                                              f'`.setrank <rank> <{programmes_helper.get_ids_string()}>`')
                return
            except DateIncorrectError:
                await ctx.send(user.mention + ' There\'s no need to set the offer date as your rank is within the '
                                              'programme limit.')
                return

        await ctx.send(user.mention + ' Offer date set. Thank you.')

    @setofferdate.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError) \
                or isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.setofferdate <day> <month> '
                                          f'<{programmes_helper.get_ids_string()}> [year]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(SetofferdateCommand(bot))
