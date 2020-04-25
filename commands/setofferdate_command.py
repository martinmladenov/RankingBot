from discord.ext import commands
from database import db_exec, db_fetchall
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
            row = db_fetchall('SELECT rank FROM ranks WHERE user_id = %s AND programme = %s', (str(user.id), programme))

            if not row:
                await ctx.send(user.mention + ' Before setting an offer date, please set your rank first using '
                                              f'`.setrank <rank> <{programmes_util.get_ids_string()}>`')
                return

            db_exec('UPDATE ranks SET offer_date = %s WHERE user_id = %s AND programme = %s',
                    (offer_date, str(user.id), programme))
            await ctx.send(user.mention + ' Offer date set. Thank you.')
        except:
            await ctx.send(user.mention + ' An error occurred while setting offer date.')

    @setofferdate.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError) \
                or isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            user = ctx.message.author
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.setofferdate <day> <month> '
                                          f'<{programmes_util.get_ids_string()}>`')
