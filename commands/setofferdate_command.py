from discord.ext import commands
from utils.offer_date_util import parse_offer_date
from utils import programmes_util


class SetofferdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setofferdate(self, ctx, day: str, month: str, programme: str):
        user = ctx.message.author

        if programme not in programmes_util.programmes:
            raise commands.UserInputError

        offer_date = parse_offer_date(day, month)

        try:
            rank = await self.bot.db_conn.fetchval('SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2',
                                                   str(user.id), programme)

            if not rank:
                await ctx.send(user.mention + ' Before setting an offer date, please set your rank first using '
                                              f'`.setrank <rank> <{programmes_util.get_ids_string()}>`')
                return

            if rank <= programmes_util.programmes[programme].places:
                await ctx.send(user.mention + ' There\'s no need to set the offer date as your rank is within the '
                                              'programme limit.')
                return

            await self.bot.db_conn.execute('UPDATE ranks SET offer_date = $1 WHERE user_id = $2 AND programme = $3',
                                           offer_date, str(user.id), programme)
            await ctx.send(user.mention + ' Offer date set. Thank you.')
        except:
            await ctx.send(user.mention + ' An error occurred while setting offer date.')

    @setofferdate.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError) \
                or isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.setofferdate <day> <month> '
                                          f'<{programmes_util.get_ids_string()}>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(SetofferdateCommand(bot))
