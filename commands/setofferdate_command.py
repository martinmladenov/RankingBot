from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option, create_choice
from utils import command_option_type
from helpers import programmes_helper
from services import ranks_service
from services.errors.entry_not_found_error import EntryNotFoundError
from services.errors.date_incorrect_error import DateIncorrectError
import constants
from datetime import date


class SetofferdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='setofferdate',
           description='Set the date you received an offer on Studielink to help people predict when they '
                       'might get theirs',
           options=[
               create_option(
                   name='day',
                   description='The day when you received your offer',
                   option_type=command_option_type.INTEGER,
                   required=True
               ),
               create_option(
                   name='month',
                   description='The month when you received your offer',
                   option_type=command_option_type.INTEGER,
                   required=True,
                   choices=[
                       create_choice(name='April', value=4),
                       create_choice(name='May', value=5),
                       create_choice(name='June', value=6),
                       create_choice(name='July', value=7),
                       create_choice(name='August', value=8)
                   ]
               ),
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
               )
           ], guild_ids=programmes_helper.get_guild_ids())
    async def setofferdate(self, ctx: SlashContext, day: int, month: int, programme: str, year: int = None):
        if year is None:
            year = constants.current_year

        user = ctx.author

        try:
            offer_date = date(year, month, day)
        except ValueError:
            await ctx.send(user.mention + ' Invalid command arguments.')
            return

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            try:
                await ranks.set_offer_date(str(user.id), programme, offer_date, year)
            except EntryNotFoundError:
                await ctx.send(user.mention + ' Before setting an offer date, please set your rank first using '
                                              '`/setrank`')
                return
            except DateIncorrectError:
                await ctx.send(user.mention + ' There\'s no need to set the offer date as your rank is within the '
                                              'programme limit.')
                return

        await ctx.send(user.mention + ' Offer date set. Thank you.')


def setup(bot):
    bot.add_cog(SetofferdateCommand(bot))
