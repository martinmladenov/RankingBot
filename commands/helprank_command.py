from discord.ext import commands
from utils import programmes_util


class HelprankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def helprank(self, ctx):
        await ctx.send(
            '**Commands:**\n'
            f'`.setrank <rank> <{programmes_util.get_ids_string()}>` Sets your rank for the specified programme\n'
            f'`.ranks` Displays all ranks\n'
            f'`.clearrank <all/{programmes_util.get_ids_string()}>` Clears your rank for all programmes\n'
            f'`.helprank` Displays this message\n'
            f'`.setofferdate <day> <month> <{programmes_util.get_ids_string()}>` Sets the date you\'ve received an offer '
            'on Studielink to help other applicants predict when they might receive one\n'
        )
