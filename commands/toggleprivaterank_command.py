from discord.ext import commands

from helpers import programmes_helper
from services import ranks_service


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggleprivaterank(self, ctx, programme: str = None):
        user = ctx.message.author
        user_id = str(user.id)

        async with self.bot.db_conn.acquire() as connection:
            ranks = ranks_service.RanksService(connection)

            is_private = await ranks.get_is_private(user_id)

            if programme is None and await ranks.get_has_only_one_rank(user_id):
                await ranks.set_is_private(user_id, not is_private)
                return

            is_private_programme = await ranks.get_is_private_programme(user_id, programme)
            if is_private_programme is None:
                await ctx.send(user.mention + ' You haven\'t set your ranking number yet.')
                return

            await ranks.set_is_private_programme(user_id, not is_private, programme)

            await ctx.send(user.mention + f' Your rank is {"no longer" if is_private else "now"} hidden from `.ranks`')

    @toggleprivaterank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError) or isinstance(error, ValueError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.toggleprivaterank '
                                          f'<{programmes_helper.get_ids_string()}>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(ToggleprivaterankCommand(bot))
