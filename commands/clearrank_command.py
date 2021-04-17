from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option, create_choice
from utils import command_option_type
from helpers import programmes_helper
from services import ranks_service


class ClearrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='clearrank',
           description='Delete your ranking number and the corresponding offer date (if it exists) from the bot',
           options=[
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=True,
                   choices=programmes_helper.get_programme_choices()
                           + [create_choice(name='All programmes', value='all')]
               ),
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=True,
                   choices=programmes_helper.get_year_choices()
               )
           ])
    async def clearrank(self, ctx: SlashContext, programme: str, year: int):
        user = ctx.author

        if programme == 'all':
            programme = None

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            await ranks.delete_rank(str(user.id), programme, year)

        await ctx.send(user.mention + ' Rank cleared.')


def setup(bot):
    bot.add_cog(ClearrankCommand(bot))
