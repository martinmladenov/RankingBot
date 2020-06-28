from discord.ext import commands
from utils import programmes_util


class ClearrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clearrank(self, ctx, programme: str):
        user = ctx.message.author

        if programme == 'all':
            clear_all = True
        elif programme in programmes_util.programmes:
            clear_all = False
        else:
            raise commands.UserInputError

        try:

            if clear_all:
                await self.bot.db_conn.execute('DELETE FROM ranks WHERE user_id = $1', str(user.id))
            else:
                await self.bot.db_conn.execute('DELETE FROM ranks WHERE user_id = $1 AND programme = $2',
                                               str(user.id), programme)

            await ctx.send(user.mention + ' Rank cleared.')
        except:
            await ctx.send(user.mention + ' An error occurred while clearing your rank.')
            raise

    @clearrank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(
                user.mention + f' Invalid arguments. Usage: `.clearrank <all/{programmes_util.get_ids_string()}>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(ClearrankCommand(bot))
