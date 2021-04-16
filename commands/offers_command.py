from discord.ext import commands
import discord
from utils import offer_date_util
from helpers import programmes_helper
from services import offers_service
import constants


class OffersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def offers(self, ctx, year: int = None, programme_id: str = None, graph_type: str = None):
        if year is None:
            year = constants.current_year

        if programme_id is not None and programme_id != 'all':
            if programme_id not in programmes_helper.programmes or \
                    (graph_type is not None and graph_type != 'step'):
                raise commands.UserInputError

            try:
                await self.send_graph(ctx, programmes_helper.programmes[programme_id], graph_type == 'step', year)
            except ValueError:
                raise commands.UserInputError

            return

        async with (await self.bot.get_db_conn()).acquire() as connection:
            offers_svc = offers_service.OffersService(connection)
            offers = await offers_svc.get_highest_ranks_with_offers(year)

        embed = discord.Embed(title=f"Highest known ranks with offers ({year})", color=0x36bee6)

        for offer in offers:
            programme = programmes_helper.programmes[offer[0]]
            rank = offer[1]
            date_str = offer_date_util.format_offer_date(offer[2])
            is_private = offer[3] is True

            embed.add_field(name=f'**{programme.icon} {programme.uni_name}\n{programme.display_name.ljust(33, " ")}**',
                            value=f'**{(("≈" + str(offers_service.round_rank(rank))) if is_private else str(rank))}**'
                                  f' on {date_str}',
                            inline=True)

        any_rounded = any(map(lambda x: x[3] is True, offers))

        embed.add_field(name='_This data has been provided by server members.' +
                             (' Some ranking numbers (as indicated '
                              'by **≈** in front of them) have been rounded to the nearest multiple of 5 '
                              'to help protect users\' privacy._' if any_rounded else '_'),
                        value='To view all commands, type `.help`\n'
                              'To add the date you\'ve received an offer, type '
                              f'`.setofferdate <day> <month> <{programmes_helper.get_ids_string()}>`',
                        inline=False)

        await ctx.send(embed=embed)

    @offers.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: '
                                          f'`.offers [year] [all/{programmes_helper.get_ids_string()}] [step]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise

    async def send_graph(self, ctx, programme: programmes_helper.Programme, step: bool, year: int):
        async with (await self.bot.get_db_conn()).acquire() as connection:
            offers = offers_service.OffersService(connection)
            await offers.generate_graph(programme, step, year)
        image = discord.File(offers_service.filename)
        await ctx.send(file=image)


def setup(bot):
    bot.add_cog(OffersCommand(bot))
