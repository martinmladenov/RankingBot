from discord.ext import commands
from database import db_exec


class ClearrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clearrank(self, ctx):
        user = ctx.message.author

        try:
            db_exec('delete from ranks where user_id = %s', (str(user.id),))
            await ctx.send(user.mention + ' Rank cleared.')
        except:
            await ctx.send(user.mention + ' An error occurred while clearing your rank.')
            raise

    @clearrank.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.clearrank`')
