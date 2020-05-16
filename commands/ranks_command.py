from discord.ext import commands
import discord
from database import db_fetchall
from utils import programmes_util


class RanksCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ranks(self, ctx):
        rows = db_fetchall('SELECT username, rank, programme FROM ranks '
                           'JOIN user_data ON ranks.user_id = user_data.user_id '
                           'WHERE (is_private IS NULL OR is_private = FALSE) AND username IS NOT NULL '
                           'ORDER BY rank ASC')

        curr_programmes = set(map(lambda x: x[2], rows))
        grouped_ranks = [(p, [row for row in rows if row[2] == p]) for p in curr_programmes]

        grouped_ranks.sort(key=lambda g: len(g[1]), reverse=True)

        is_bot_channel = not ctx.guild or 'bot' in ctx.message.channel.name

        group_truncated = {}

        if not is_bot_channel:
            for i in range(len(grouped_ranks)):
                group_name = grouped_ranks[i][0]
                truncated_list = grouped_ranks[i][1][:10]
                group_truncated[group_name] = len(grouped_ranks[i][1]) - 10
                grouped_ranks[i] = (group_name, truncated_list)

        embed = discord.Embed(title="Ranking numbers", color=0x36bee6)

        for group in grouped_ranks:
            programme = programmes_util.programmes[group[0]]
            embed.add_field(name=f'**{programme.icon} {programme.uni_name}\n{programme.display_name.ljust(33, " ")}**',
                            value=('\n'.join(('`' + (' ' * (3 - len(str(x[1])))) + str(x[1]) + f' {x[0]}`')
                                             for x in group[1])) +
                                  (f'\n**_+ {group_truncated[group[0]]} more..._**'
                                   if not is_bot_channel and group_truncated[group[0]] > 0 else ''),
                            inline=True)

        if any(x > 0 for x in group_truncated.values()):
            embed.add_field(name='**_List is truncated_**',
                            value='**To view the full list, please type this command in a bot channel, such as '
                                  '<#556533405794172939>**\n',
                            inline=False)

        embed.add_field(name='_Please note: This bot is purely for fun, the ranking numbers do not'
                             ' represent performance at university_',
                        value=f'To view all commands, type `.help`\n'
                              f'To set your ranking number, type `.setrank <rank> <{programmes_util.get_ids_string()}>`',
                        inline=False)

        await ctx.send(embed=embed)

    @ranks.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.ranks`')
        raise error
