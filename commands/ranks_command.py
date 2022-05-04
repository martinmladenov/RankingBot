from discord.ext import commands
import discord
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type
from helpers import programmes_helper
from services import ranks_service
from utils.response_building_util import build_embed_groups
import constants


class RanksCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name='ranks',
           description='Show all public ranks (not necessarily accepted)',
           options=[
               create_option(
                   name='year',
                   description='Year of application',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               ),
               create_option(
                   name='public',
                   description='Show the result of the command to everyone',
                   option_type=command_option_type.BOOLEAN,
                   required=False,
               )
           ])
    async def ranks(self, ctx: SlashContext, year: int = None, public: bool = False):

        if year is None:
            year = constants.current_year

        async with (await self.bot.get_db_conn()).acquire() as connection:
            ranks = ranks_service.RanksService(connection)
            grouped_ranks = await ranks.get_top_ranks(year)

        is_bot_channel = not ctx.guild or 'bot' in ctx.channel.name
        if (is_bot_channel):
            public = True

        group_truncated = {}

        if not is_bot_channel:
            for i in range(len(grouped_ranks)):
                group_name = grouped_ranks[i][0]
                truncated_list = grouped_ranks[i][1][:10]
                group_truncated[group_name] = len(grouped_ranks[i][1]) - 10
                grouped_ranks[i] = (group_name, truncated_list)

        embed_dict = dict()

        for group in grouped_ranks:
            programme = programmes_helper.programmes[group[0]]
            group_name = f'**{programme.icon} {programme.uni_name}\n{programme.display_name.ljust(33, " ")}**'
            group_list = list(('`' + (' ' * (3 - len(str(x[1])))) + str(x[1]) + f' {x[0]}`')
                              for x in group[1])
            if not is_bot_channel and group_truncated[group[0]] > 0:
                group_list.append(f'\n**_+ {group_truncated[group[0]]} more..._**')

            embed_dict[group_name] = group_list

        embed = discord.Embed(title=f"Ranking numbers ({year})", color=0x36bee6)

        embed.add_field(name='Note: Not everyone in this list has received an offer.',
                        value='To view the highest known ranking numbers with offers, use `/offers`.',
                        inline=False)

        build_embed_groups(embed, embed_dict)

        if any(x > 0 for x in group_truncated.values()):
            embed.add_field(name='**_List is truncated_**',
                            value='To view the full list, please use this command in a bot channel, such as '
                                  '<#556533405794172939>\n',
                            inline=False)

        embed.add_field(name='To set your ranking number, use `/setrank`.',
                        value='_Please note: This command is purely for fun, the ranking numbers do not'
                              ' represent performance at university_',
                        inline=False)

        await ctx.send(embed=embed, hidden=not public)


def setup(bot):
    bot.add_cog(RanksCommand(bot))
