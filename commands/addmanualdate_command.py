from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option, create_choice
from utils import command_option_type
from datetime import date
from helpers import programmes_helper
from services import ranks_service
from services.errors.date_incorrect_error import DateIncorrectError
import constants


class AddmanualdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='addmanualdate',
           description='Manually add the date of an offer which is __not__ yours '
                       '(for example, one that you found online)',
           options=[
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=True,
                   choices=programmes_helper.get_programme_choices()
               ),
               create_option(
                   name='rank',
                   description='Ranking number',
                   option_type=command_option_type.INTEGER,
                   required=True
               ),
               create_option(
                   name='day',
                   description='The day of the offer',
                   option_type=command_option_type.INTEGER,
                   required=True
               ),
               create_option(
                   name='month',
                   description='The month of the offer',
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
                   name='source',
                   description='Source of the data (e.g. reddit, whatsapp...)',
                   option_type=command_option_type.STRING,
                   required=False
               ),
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               )
           ])
    async def addmanualdate(self, ctx: SlashContext, programme: str, rank: int, day: int, month: int,
                            source: str = None, year: int = None):
        user = ctx.author

        if not ctx.guild:
            await ctx.send(user.mention + ' You don\'t have permission to execute this command via DM')
            return

        if not source:
            source = 'manual'

        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            tr = connection.transaction()
            await tr.start()

            try:
                offer_date = date(year, month, day)
                await ranks.add_rank(rank, programme, year, offer_date=offer_date, source=source)

                if rank <= programmes_helper.programmes[programme].places[year]:
                    raise DateIncorrectError

                await tr.commit()
                await ctx.send(user.mention + ' Rank and offer date added.')

            except DateIncorrectError:
                await tr.rollback()
                await ctx.send(user.mention + ' There\'s no need to set this offer date as this rank is '
                                              'within the programme limit.')
            except ValueError:
                await tr.rollback()
                await ctx.send(user.mention + ' Invalid command arguments.')
            except:
                await tr.rollback()
                raise


def setup(bot):
    bot.add_cog(AddmanualdateCommand(bot))
