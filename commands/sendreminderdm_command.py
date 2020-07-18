import discord
from discord.ext import commands
from utils import response_building_util
from helpers import programmes_helper
from services import dm_service
import constants
from datetime import datetime, timedelta


class SendreminderdmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sendreminderdm(self, ctx, age_days: int, dry_run: str = None):

        if ctx.message.author.id != constants.administrator_user_id or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        send_messages = True

        if dry_run is not None:
            if dry_run == 'dry-run':
                send_messages = False
                await ctx.send(ctx.message.author.mention + f' dry run: not sending DMs')
            else:
                raise commands.UserInputError

        date = datetime.utcnow() - timedelta(days=age_days)

        async with self.bot.db_conn.acquire() as connection:
            dm = dm_service.DMService(connection)

            user_data_arr = await dm.get_users_with_active_dm_sent_before_date(date)

            await ctx.send(ctx.message.author.mention + f' Sending DMs to {len(user_data_arr)} users...')

            results = {
                'success': [],
                'user-not-found': [],
                'unhandled-exception': [],
                'cannot-send-dm': [],
            }

            for user_data in user_data_arr:
                user_id = user_data[0]
                programme_id = user_data[1]
                username = user_data[2]

                try:
                    user = self.bot.get_user(int(user_id))

                    if not user:
                        results['user-not-found'].append(f'{username} ({user_id})')
                        continue

                    key = True
                    if send_messages:
                        key = await dm.send_programme_rank_reminder_dm(
                            user, programmes_helper.programmes[programme_id])

                    results['success' if key else 'cannot-send-dm'].append(f'{username}: {programme_id}')
                except Exception as e:
                    print(f'an error occurred while sending message to {username}: {str(e)}')
                    results['unhandled-exception'].append(f'{username} ({user_id})')

        await ctx.send(ctx.message.author.mention + f' Done sending DMs, '
                                                    f'{len(user_data_arr) - len(results["success"])} skipped')

        if not results['success']:
            return

        results_embed = discord.Embed(title=f".sendreminderdm results", color=0x36bee6)

        user_groups = dict()

        for key in results.keys():
            user_groups[key] = list(f'`{u}`' for u in results[key]) if results[key] else ['_None_']

        response_building_util.build_embed_groups(results_embed, user_groups)

        if dry_run:
            results_embed.set_footer(text='dry run: not sending DMs')

        dm_channel = await ctx.message.author.create_dm()
        await dm_channel.send(embed=results_embed)

    @sendreminderdm.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.sendreminderdm '
                                          '<minimal age of previous DM in days> [dry-run]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(SendreminderdmCommand(bot))
