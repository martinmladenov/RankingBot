from discord.ext import commands
import discord
from utils import programmes_util, offer_date_util, offer_plot_util


class OffersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def offers(self, ctx, programme_id: str = None):
        if programme_id is not None:
            if programme_id not in programmes_util.programmes:
                raise commands.UserInputError

            await self.send_graph(ctx, programmes_util.programmes[programme_id])

            return

        rows = await self.bot.db_conn.fetch(
            'select r.programme, r.rank, MAX(d.offer_date), ud.is_private '
            'from (select programme, max(rank) as rank from ranks '
            'where ranks.offer_date is not null '
            'group by programme) as r '
            'inner join ranks as d '
            'on r.programme = d.programme and r.rank = d.rank '
            'and d.offer_date is not null '
            'left join user_data ud on d.user_id = ud.user_id '
            'group by r.programme, r.rank, ud.is_private '
            'order by MAX(d.offer_date) desc')

        embed = discord.Embed(title="Highest known ranks with offers", color=0x36bee6)

        for offer in rows:
            programme = programmes_util.programmes[offer[0]]
            rank = offer[1]
            date_str = offer_date_util.format_offer_date(offer[2])
            is_private = offer[3] is True

            embed.add_field(name=f'**{programme.icon} {programme.uni_name}\n{programme.display_name.ljust(33, " ")}**',
                            value=f'**{(("≈" + str(offer_plot_util.round_rank(rank))) if is_private else str(rank))}**'
                                  f' on {date_str}',
                            inline=True)

        any_rounded = any(map(lambda x: x[3] is True, rows))

        embed.add_field(name='_This data has been provided by server members.' +
                             (' Some ranking numbers (as indicated '
                              'by **≈** in front of them) have been rounded to the nearest multiple of 5 '
                              'to help protect users\' privacy._' if any_rounded else '_'),
                        value='To view all commands, type `.help`\n'
                              'To add the date you\'ve received an offer, type '
                              f'`.setofferdate <day> <month> <{programmes_util.get_ids_string()}>`',
                        inline=False)

        await ctx.send(embed=embed)

    @offers.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.offers [{programmes_util.get_ids_string()}]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise

    async def send_graph(self, ctx, programme: programmes_util.Programme):
        await offer_plot_util.generate_graph(programme, self.bot.db_conn)
        image = discord.File(offer_plot_util.filename)
        await ctx.send(file=image)


def setup(bot):
    bot.add_cog(OffersCommand(bot))
