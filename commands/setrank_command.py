from discord.ext import commands
from database import db_exec


class SetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setrank(self, ctx, rank_number: int):
        user = ctx.message.author

        try:
            db_exec('INSERT INTO ranks (user_id, username, rank) VALUES (%s, %s, %s)',
                    (user.id, user.name, rank_number))
            await ctx.send(user.mention + ' Rank set.')
        except:
            await ctx.send(user.mention + ' Unable to set rank.'
                                          ' If you have already set a rank, try clearing it using `.clearrank`')
            # raise

    @setrank.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.setrank <rank>`')
