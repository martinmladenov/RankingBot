from discord.ext import commands

from helpers import programmes_helper
from services import ranks_service
import constants


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggleprivaterank(self, ctx, programme: str = None, year: int = None):
        user = ctx.message.author
        user_id = str(user.id)

        if year is None:
            year = constants.current_year

        async with self.bot.db_conn.acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            if programme is None and await ranks.get_has_only_one_rank(user_id, year):
                is_private = await ranks.get_is_private(user_id, year)
                await ranks.set_is_private(user_id, not is_private, year)
            else:
                if programme not in programmes_helper.programmes:
                    raise commands.UserInputError

                is_private = await ranks.get_is_private_programme(user_id, programme, year)
                if is_private is None:
                    await ctx.send(user.mention + ' You haven\'t set your ranking number for this programme yet.')
                    return

                await ranks.set_is_private_programme(user_id, not is_private, programme, year)

            await ctx.send(user.mention + f' Your rank is {"no longer" if is_private else "now"} hidden from `.ranks`')

    @toggleprivaterank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.toggleprivaterank '
                                          f'<{programmes_helper.get_ids_string()}> [year]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(ToggleprivaterankCommand(bot))
