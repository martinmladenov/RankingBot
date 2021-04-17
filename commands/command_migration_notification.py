from discord.ext import commands


class CommandMigrationNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['addmanualdate',
                               'clearrank',
                               'offergraph',
                               'offers',
                               'ranks',
                               'setofferdate',
                               'setrank',
                               'toggleprivaterank'])
    async def migration_notification(self, ctx: commands.Context):
        cmd = ctx.message.content.split(' ')[0][1:]
        await ctx.send(ctx.message.author.mention +
                       ' We now use Discord\'s new Slash Commands. '
                       f'This command is now `/{cmd}`. '
                       f'After typing `/{cmd}`, you can press `TAB` to choose arguments.')


def setup(bot):
    bot.add_cog(CommandMigrationNotification(bot))
