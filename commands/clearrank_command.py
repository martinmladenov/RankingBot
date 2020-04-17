from discord.ext import commands
from database import db_exec


class ClearrankCommand(commands.Cog):
    def __init__(self, bot, programmes):
        self.bot = bot
        self.programmes = programmes

    @commands.command()
    async def clearrank(self, ctx, programme: str):
        user = ctx.message.author

        if programme == 'all':
            clear_all = True
        elif programme in self.programmes:
            clear_all = False
        else:
            raise commands.UserInputError

        try:

            if clear_all:
                db_exec('DELETE FROM ranks WHERE user_id = %s', (str(user.id),))
            else:
                db_exec('DELETE FROM ranks WHERE user_id = %s AND programme = %s', (str(user.id), programme))

            await ctx.send(user.mention + ' Rank cleared.')
        except:
            await ctx.send(user.mention + ' An error occurred while clearing your rank.')
            raise

    @clearrank.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.clearrank <all/{"/".join(self.programmes)}>`')
