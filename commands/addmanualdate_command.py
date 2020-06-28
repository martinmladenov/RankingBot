from discord.ext import commands
from utils import programmes_util, offer_date_util


class AddmanualdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addmanualdate(self, ctx, programme: str, rank_number: int, day: str, month: str):
        user = ctx.message.author

        if not ctx.guild:
            await ctx.send(user.mention + ' You don\'t have permission to execute this command')
            return

        if rank_number <= 0 or rank_number >= 10000 or programme not in programmes_util.programmes:
            raise commands.UserInputError

        if rank_number <= programmes_util.programmes[programme].places:
            await ctx.send(user.mention + ' There\'s no need to set the offer date as this rank is within the '
                                          'programme limit.')
            return

        offer_date = offer_date_util.parse_offer_date(day, month)

        try:
            await self.bot.db_conn.execute('INSERT INTO ranks (rank, programme, offer_date) VALUES ($1, $2, $3)',
                                           rank_number, programme, offer_date)
            await ctx.send(user.mention + ' Rank and offer date added.')
        except:
            await ctx.send(user.mention + ' Unable to add offer date.')

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
