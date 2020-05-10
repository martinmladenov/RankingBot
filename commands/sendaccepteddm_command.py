import discord
from discord.ext import commands
from utils import dm_util, programmes_util
import constants


class SendaccepteddmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sendaccepteddm(self, ctx, uni_name: str, dry_run: str = None):

        if ctx.message.author.id != constants.administrator_user_id or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        if uni_name == 'all':
            for uni in ('TUD', 'TUE'):
                await ctx.send(ctx.message.author.mention + f' Processing {uni}')
                await self.sendaccepteddm(ctx, uni, dry_run)
            return

        if uni_name not in dm_util.University.__members__:
            raise commands.UserInputError

        send_messages = True

        if dry_run is not None:
            if dry_run == 'dry-run':
                send_messages = False
                await ctx.send(ctx.message.author.mention + f' dry run: not sending DMs')
                print('Dry run')
            else:
                raise commands.UserInputError

        university = dm_util.University[uni_name]

        channel_id = constants.accepted_channel_id
        message_id = constants.accepted_message_id

        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        if university == dm_util.University.TUD:
            target_emoji_name = 'TUD'
        elif university == dm_util.University.TUE:
            target_emoji_name = 'TuE'
        else:
            raise commands.UserInputError

        reaction = None
        for curr_reaction in message.reactions:
            if curr_reaction.custom_emoji and curr_reaction.emoji.name == target_emoji_name:
                reaction = curr_reaction
                break

        users = await reaction.users().flatten()

        await ctx.send(ctx.message.author.mention + f' Sending DMs to {len(users)} users...')
        print("Sending DMs")

        success = 0

        for member in users:
            if not isinstance(member, discord.Member):
                print(f'skipping {member.name}: not server member')
                continue

            programme_id = dm_util.get_member_programme(member, university)

            if not programme_id:
                print(f'skipping {member.name}: unknown programme')
                continue

            try:
                result = await dm_util.send_programme_rank_dm(
                    member, programmes_util.programmes[programme_id], send_messages)

                if result:
                    success += 1
            except Exception as e:
                print(f'an error occurred while sending message to {member.name}: {str(e)}')

        await ctx.send(ctx.message.author.mention + f' Done sending DMs, {len(users) - success} skipped')
        print('Done sending DMs')

    @sendaccepteddm.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.sendaccepteddm <all/TUD/TUE> [dry-run]`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise
