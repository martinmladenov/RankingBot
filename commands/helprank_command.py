from discord.ext import commands


class HelprankCommand(commands.Cog):
    def __init__(self, bot, programmes):
        self.bot = bot
        self.programmes = programmes

    @commands.command()
    async def helprank(self, ctx):
        await ctx.send(
            '**Commands:**\n'
            f'`.setrank <rank> <{"/".join(self.programmes)}>` Sets your rank for the specified programme\n'
            f'`.ranks` Displays all ranks\n'
            f'`.clearrank` Clears your rank for all programmes\n'
            f'`.helprank` Displays this message\n'
        )
