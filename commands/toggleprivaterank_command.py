from discord.ext import commands
from services import user_data_service


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggleprivaterank(self, ctx):
        user = ctx.message.author
        user_id = str(user.id)

        async with self.bot.db_conn.acquire() as connection:
            users = user_data_service.UserDataService(connection)

            is_private = await users.get_is_private(user_id)

            if is_private is None:
                await ctx.send(user.mention + ' You haven\'t set your ranking number yet.')
                return

            await users.set_is_private(user_id, not is_private)

            await ctx.send(user.mention + f' Your rank is {"no longer" if is_private else "now"} hidden from `.ranks`')

    @toggleprivaterank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.toggleprivaterank`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(ToggleprivaterankCommand(bot))
