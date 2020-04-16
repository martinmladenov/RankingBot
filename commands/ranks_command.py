from discord.ext import commands
import discord
from database import db_fetchall


class RanksCommand(commands.Cog):
    def __init__(self, bot, programmes):
        self.bot = bot
        self.programmes = programmes

    @commands.command()
    async def ranks(self, ctx):
        rows = db_fetchall('SELECT username, rank, programme FROM ranks ORDER BY rank ASC')

        curr_programmes = set(map(lambda x: x[2], rows))
        grouped_ranks = [(p, [row for row in rows if row[2] == p]) for p in curr_programmes]

        grouped_ranks.sort(key=lambda g: len(g[1]), reverse=True)

        embed = discord.Embed(title="Top ranks", color=0x36bee6)

        for group in grouped_ranks:
            embed.add_field(name=f'**{group[0]}**',
                            value=('\n'.join(('`' + (' ' * (3 - len(str(x[1])))) + str(x[1]) + f' {x[0]}`')
                                             for x in group[1])),
                            inline=True)

        embed.add_field(name='_Please note: This bot is purely for fun, the ranking numbers do not'
                             ' represent performance at university_',
                        value=f'To set your rank, type `.setrank <rank> <{"/".join(self.programmes)}>`',
                        inline=False)

        await ctx.send(embed=embed)

    @ranks.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            user = ctx.message.author
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.ranks`')
