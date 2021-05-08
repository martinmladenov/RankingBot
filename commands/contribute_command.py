import os
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from helpers import programmes_helper


class ContributeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='contribute',
           description='Display information about helping the development of the bot', guild_ids=programmes_helper.get_guild_ids())
    async def contribute(self, ctx: SlashContext):
        await ctx.send('The bot is open-source. You can find the source code '
                       '_[on its GitHub repository](https://github.com/martinmladenov/RankingBot/)_.\n'
                       'Feel free to contribute by creating an issue or submitting a pull request!')


def setup(bot):
    bot.add_cog(ContributeCommand(bot))
