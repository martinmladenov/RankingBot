from discord.ext import commands
import discord
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type
from utils import offer_date_util
from helpers import programmes_helper
from services import offers_service
import constants


class OffersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='offers',
           description='Show highest known ranks with offers',
           options=[
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               )
           ], guild_ids=programmes_helper.get_guild_ids())
    async def offers(self, ctx: SlashContext, year: int = None):
        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            offers_svc = offers_service.OffersService(connection)
            offers = await offers_svc.get_highest_ranks_with_offers(year)

        embed = discord.Embed(
            title=f"Highest known ranks with offers ({year})", color=0x36bee6)

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

        embed.add_field(name='To see a graph of ranking numbers and the dates when they received offers,'
                             ' use `/offergraph`.',
                        value='This data has been provided by server members.' +
                              (' Some ranking numbers (as indicated '
                               'by **≈** in front of them) have been rounded to the nearest multiple of 5 '
                               'to help protect users\' privacy.' if any_rounded else '') +
                              '\nTo set your ranking number, use `/setrank`. '
                              'Then, to set the date you received an offer, use `/setofferdate`.',
                        inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OffersCommand(bot))
