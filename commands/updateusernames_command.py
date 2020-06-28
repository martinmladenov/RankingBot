import discord
from discord.ext import commands
import constants


class UpdateusernamesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def updateusernames(self, ctx, dry_run: str = None):

        if ctx.message.author.id != constants.administrator_user_id or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        save_changes = True

        if dry_run is not None:
            if dry_run == 'dry-run':
                save_changes = False
                await ctx.send(ctx.message.author.mention + f' dry run: not saving changes to database')
            else:
                raise commands.UserInputError

        user_data_rows = await self.bot.db_conn.fetch('SELECT user_id, username FROM user_data')

        guild_members = dict(map(lambda x: (str(x.id), x.name), ctx.guild.members))

        await ctx.send(ctx.message.author.mention + f' Checking {len(user_data_rows)} users...')

        results = {
            'success': [],
            'user-not-found': []
        }

        for user_data_row in user_data_rows:
            user_id = user_data_row[0]
            stored_username = user_data_row[1]

            if user_id not in guild_members.keys():
                results['user-not-found'].append(f'{stored_username} ({user_id})')
                continue

            actual_username = guild_members[user_id]

            if stored_username == actual_username:
                continue

            if save_changes:
                await self.bot.db_conn.execute('UPDATE user_data SET username = $1 WHERE user_id = $2', actual_username,
                                               user_id)

            results['success'].append(f'{stored_username} → {actual_username}')

        await ctx.send(ctx.message.author.mention + ' Done checking users, '
                                                    f'{len(results["success"])} usernames updated')

        results_embed = discord.Embed(title=f".updateusernames results", color=0x36bee6)

        for result in results.keys():
            user_string = '\n'.join(f'`{u}`' for u in results[result]) if results[result] else '_None_'
            results_embed.add_field(name=result, value=user_string, inline=True)

        if dry_run:
            results_embed.set_footer(text='dry run: not saving changes to database')

        dm_channel = await ctx.message.author.create_dm()
        await dm_channel.send(embed=results_embed)

    @updateusernames.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.updateusernames [dry-run]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(UpdateusernamesCommand(bot))
