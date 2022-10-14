from discord.ext import commands
import discord
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type
from helpers import programmes_helper
from services import offers_service
import constants


class OffergraphCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='offergraph',
           description='Show a graph of ranking numbers and the dates when they received offers',
           options=[
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=True,
                   choices=programmes_helper.get_programme_choices()
               ),
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               ),
               create_option(
                   name='approx',
                   description='Show approximation line',
                   option_type=command_option_type.BOOLEAN,
                   required=False
               ),
               create_option(
                   name='public',
                   description='Show the result of the command to everyone',
                   option_type=command_option_type.BOOLEAN,
                   required=False,
               )
           ])
    async def offergraph(self, ctx: SlashContext, programme: str, year: int = None,
                         approx: bool = True, public: bool = False):
        if year is None:
            year = constants.current_year

        if not ctx.guild or 'bot' in ctx.channel.name:
            public = True

        # Show "Bot is thinking" message
        await ctx.defer(hidden=not public)

        async with (await self.bot.get_db_conn()).acquire() as connection:
            offers = offers_service.OffersService(connection)
            try:
                filename = await offers.generate_graph(programmes_helper.programmes[programme], not approx, year)
            except ValueError:
                await ctx.send('This programme was not numerus fixus in ' + str(year), hidden=not public)
                return
        image = discord.File(filename)
        await ctx.send(file=image, hidden=not public)
        await offers.clean_up_file(filename)


def setup(bot):
    bot.add_cog(OffergraphCommand(bot))
