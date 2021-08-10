from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type

from helpers import programmes_helper, config_helper
from services import ranks_service
import constants


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='toggleprivaterank',
           description='Toggle whether your rank is displayed to other people',
           options=[
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=False,
                   choices=programmes_helper.get_programme_choices()
               ),
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               )
           ], guild_ids=config_helper.get_guild_ids())
    async def toggleprivaterank(self, ctx: SlashContext, programme: str = None, year: int = None):
        user = ctx.author
        user_id = str(user.id)

        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            if programme is None and await ranks.get_has_only_one_rank(user_id, year):
                is_private = await ranks.get_is_private(user_id, year)
                await ranks.set_is_private(user_id, not is_private, year)
            else:
                if programme is None:
                    await ctx.send(user.mention + ' Please specify the programme of the rank you wish to '
                                                  'toggle the visibility of.')
                    return

                is_private = await ranks.get_is_private_programme(user_id, programme, year)
                if is_private is None:
                    await ctx.send(user.mention + ' You haven\'t set your ranking number for this programme yet.')
                    return

                await ranks.set_is_private_programme(user_id, not is_private, programme, year)

            await ctx.send(user.mention + f' Your rank is {"no longer" if is_private else "now"} hidden from `.ranks`')


def setup(bot):
    bot.add_cog(ToggleprivaterankCommand(bot))
