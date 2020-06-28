from discord.ext import commands


class ToggleprivaterankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def toggleprivaterank(self, ctx):
        user = ctx.message.author

        try:
            row = await self.bot.db_conn.fetchrow('SELECT is_private FROM user_data WHERE user_id = $1', str(user.id))

            if not row:
                await self.bot.db_conn.execute(
                    'INSERT INTO user_data (user_id, username, is_private) VALUES ($1, $2, $3)',
                    str(user.id), user.name, True)
                await ctx.send(user.mention + ' Your rank is now hidden from `.ranks`')
                return

            if not row[0]:
                await self.bot.db_conn.execute('UPDATE user_data SET is_private = $1 WHERE user_id = $2', True,
                                               str(user.id))
                await ctx.send(user.mention + ' Your rank is now hidden from `.ranks`')
            else:
                await self.bot.db_conn.execute('UPDATE user_data SET is_private = $1 WHERE user_id = $2', False,
                                               str(user.id))
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


def setup(bot):
    bot.add_cog(ToggleprivaterankCommand(bot))
