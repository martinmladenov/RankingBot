from discord.ext import commands
from helpers import programmes_helper


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send(
            '**Commands:**\n'
            f'`.setrank <rank> <{programmes_helper.get_ids_string()}> [year]` '
            f'Sets your rank for the specified programme\n'
            f'`.ranks [year]` Displays all ranks\n'
            f'`.offers [all/{programmes_helper.get_ids_string()}] [year] [step]` '
            f'Shows the last known ranks which have received an offer\n'
            f'`.clearrank <all/{programmes_helper.get_ids_string()}> <year>` '
            f'Clears your rank for the specified programme\n'
            f'`.setofferdate <day> <month> <{programmes_helper.get_ids_string()}>` Sets the date you\'ve received'
            f' an offer on Studielink to help other applicants predict when they might receive one\n'
            f'`.toggleprivaterank <{programmes_helper.get_ids_string()}>` Toggles whether your rank is displayed on '
            f'`.ranks` for the specified programme\n'
            f'`.addmanualdate <{programmes_helper.get_ids_string()}> <rank> <day> <month> [source] [year]` '
            f'Manually adds a ranking number and a date without associating them with a user\n'
            f'`.help` Displays this message\n'
        )


def setup(bot):
    bot.add_cog(HelpCommand(bot))
