import discord
from discord.ext import commands
from utils import dm_util, programmes_util
import constants
from database import db_fetchall
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

        user_data_rows = db_fetchall('SELECT user_id, dm_programme, username FROM user_data '
                                     'WHERE dm_status = %s  '
                                     'AND dm_last_sent <= timestamp %s', (dm_util.DmStatus.AWAITING_RANK, date))

        await ctx.send(ctx.message.author.mention + f' Sending DMs to {len(user_data_rows)} users...')

        results = {
            'success': [],
            'user-not-found': [],
            'unhandled-exception': [],
            'cannot-send-dm': [],
        }

        for user_data_row in user_data_rows:
            user_id = user_data_row[0]
            programme_id = user_data_row[1]
            username = user_data_row[2]

            try:
                user = self.bot.get_user(int(user_id))

                if not user:
                    results['user-not-found'].append(f'{username} ({user_id})')
                    continue

                result = True
                if send_messages:
                    result = await dm_util.send_programme_rank_reminder_dm(
                        user, programmes_util.programmes[programme_id])

                results['success' if result else 'cannot-send-dm'].append(f'{username}: {programme_id}')
            except Exception as e:
                print(f'an error occurred while sending message to {username}: {str(e)}')
                results['unhandled-exception'].append(f'{username} ({user_id})')

        await ctx.send(ctx.message.author.mention + f' Done sending DMs, '
                                                    f'{len(user_data_rows) - len(results["success"])} skipped')

        results_embed = discord.Embed(title=f".sendreminderdm results", color=0x36bee6)

        for result in results.keys():
            user_string = '\n'.join(f'`{u}`' for u in results[result]) if results[result] else '_None_'
            results_embed.add_field(name=result, value=user_string, inline=True)

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
