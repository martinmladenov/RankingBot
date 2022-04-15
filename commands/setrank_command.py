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
           ])
    async def setrank(self, ctx: SlashContext, rank: int, programme: str, year: int = None):
        user = ctx.author
        user_id = str(user.id)

        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)
            users = user_data_service.UserDataService(connection)

            curr_rank_details = await ranks.get_rank_details_for_programme_and_user(programme, year, user_id)

            if curr_rank_details:
                curr_rank, curr_is_private = curr_rank_details
                if rank == curr_rank:
                    if not curr_is_private:
                        await ctx.send(user.mention +
                                       ' You have already set your ranking number. It can be seen via `/ranks`.' +
                                       (' If you\'re trying to set an offer date, use `/setofferdate`.'
                                        if programmes_helper.programmes[programme].places[year] < rank else ''))
                    else:
                        await ranks.set_is_private_programme(user_id, False, programme, year)
                        await ctx.send(user.mention +
                                       ' You have already set your ranking number, but it was private (you\'ve likely '
                                       'set it by replying to a direct message by the bot).\nIt has now been made '
                                       'visible and you can see it via `/ranks`. '
                                       'If you want to make it private again, you can use `/toggleprivaterank`.' +
                                       ('\nIf you\'re trying to set an offer date, you can use `/setofferdate`.'
                                        if programmes_helper.programmes[programme].places[year] < rank else ''))
                else:
                    if not curr_is_private:
                        await ctx.send(user.mention +
                                       f' You have already set a different ranking number (**{curr_rank}**). '
                                       'To change it, first clear the old one using `/clearrank` and then try setting '
                                       'the new one again.')
                    else:
                        await ctx.send(user.mention +
                                       ' You have already set a different ranking number, but it is private (you\'ve '
                                       'likely set it by replying to a direct message by the bot). '
                                       'To change it, first clear the old one using `/clearrank` and then try setting '
                                       'the new one again.')

                return

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
        await ctx.send(user.mention + ' Your ranking number was successfully added. It is now set as public and can be '
                                      'seen via `/ranks`. If you want to make it private, you can use '
                                      '`/toggleprivaterank`.' +
                       ('\nIf you have received an offer, please use `/setofferdate` to set it.'
                        if programmes_helper.programmes[programme].places[year] < rank else ''))


def setup(bot):
    bot.add_cog(SetrankCommand(bot))
