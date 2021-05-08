from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type

from services import ranks_service, user_data_service
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from helpers import programmes_helper
import constants


class SetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='setrank',
           description='Set your ranking number',
           options=[
               create_option(
                   name='rank',
                   description='Your ranking number',
                   option_type=command_option_type.INTEGER,
                   required=True
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
    async def setrank(self, ctx: SlashContext, rank: int, programme: str, year: int = None):
        user = ctx.author
        user_id = str(user.id)

        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)
            users = user_data_service.UserDataService(connection)

            tr = connection.transaction()
            await tr.start()

            try:
                try:
                    await ranks.add_rank(rank, programme, year, user_id, source='command')
                except ValueError:
                    await ctx.send(user.mention + ' Invalid command arguments.')
                    await tr.rollback()
                    return
                except EntryAlreadyExistsError:
                    await ctx.send(user.mention + ' You have already set your ranking number. To set a different one, '
                                                  'clear it using `/clearrank` and try setting it again.')
                    await tr.rollback()
                    return

                await users.add_user(user_id, user.name)

            except:
                await tr.rollback()
                raise

            await tr.commit()
        await ctx.send(user.mention + ' Rank set.')


def setup(bot):
    bot.add_cog(SetrankCommand(bot))
