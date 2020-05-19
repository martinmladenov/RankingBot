from discord.ext import commands
from database import db_exec, db_fetchall


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggleprivaterank(self, ctx):
        user = ctx.message.author

        try:
            row = db_fetchall('SELECT is_private FROM user_data WHERE user_id = %s', (str(user.id),))

            if not row:
                db_exec('INSERT INTO user_data (user_id, username, is_private) VALUES (%s, %s, %s)',
                        (str(user.id), user.name, True))
                await ctx.send(user.mention + ' Your rank is now hidden from `.ranks`')
                return

            if not row[0][0]:
                db_exec('UPDATE user_data SET is_private = %s WHERE user_id = %s', (True, str(user.id)))
                await ctx.send(user.mention + ' Your rank is now hidden from `.ranks`')
            else:
                db_exec('UPDATE user_data SET is_private = %s WHERE user_id = %s', (False, str(user.id)))
                await ctx.send(user.mention + ' Your rank is no longer hidden from `.ranks`')

        except:
            await ctx.send(user.mention + ' An error occurred while executing the command')

    @toggleprivaterank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + f' Invalid arguments. Usage: `.toggleprivaterank`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise
