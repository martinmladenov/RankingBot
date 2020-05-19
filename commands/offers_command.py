from discord.ext import commands
import discord
from database import db_fetchall
from utils import programmes_util, offer_date_util


class OffersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def offers(self, ctx):
        rows = db_fetchall('select r.programme, r.rank, d.offer_date, ud.is_private '
                           'from (select programme, max(rank) as rank from ranks '
                           'where ranks.offer_date is not null '
                           'group by programme) as r '
                           'inner join ranks as d '
                           'on r.programme = d.programme and r.rank = d.rank '
                           'and d.offer_date is not null '
                           'left join user_data ud on d.user_id = ud.user_id '
                           'order by d.offer_date desc')

        embed = discord.Embed(title="Highest known ranks with offers", color=0x36bee6)

        for offer in rows:
            programme = programmes_util.programmes[offer[0]]
            rank = offer[1]
            date_str = offer_date_util.format_offer_date(offer[2])
            is_private = offer[3] is True

            embed.add_field(name=f'**{programme.icon} {programme.uni_name}\n{programme.display_name.ljust(33, " ")}**',
                            value=f'**{(("≈" + str(round_rank(rank))) if is_private else str(rank))}** on {date_str}',
                            inline=True)

        embed.add_field(name='_This data has been provided by server members. Some ranking numbers (as indicated '
                             'by **≈** in front of them) have been rounded to the nearest multiple of 5 '
                             'to help protect users\' privacy._',
                        value='To view all commands, type `.help`\n'
                              'To add the date you\'ve received an offer, type '
                              f'`.setofferdate <day> <month> <{programmes_util.get_ids_string()}>`',
                        inline=False)

        await ctx.send(embed=embed)

    @offers.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.offers`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise



def round_rank(number, base=5):
    return base * round(number / base)
