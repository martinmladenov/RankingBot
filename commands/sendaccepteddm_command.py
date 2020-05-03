import discord
from discord.ext import commands
from utils import dm_util, programmes_util


class SendaccepteddmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sendaccepteddm(self, ctx, uni_name: str):

        if ctx.message.author.id != 403569083402158090 or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        if uni_name not in dm_util.University.__members__:
            raise commands.UserInputError

        university = dm_util.University[uni_name]

        channel_id = 539780235411980294
        message_id = 699757067702894855

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
                result = await dm_util.send_programme_rank_dm(member, programmes_util.programmes[programme_id])

                if result:
                    success += 1
            except Exception as e:
                print(f'an error occurred while sending message to {member.name}: {str(e)}')

        await ctx.send(ctx.message.author.mention + f' Done sending DMs, {len(users) - success}/{len(users)} skipped')
        print('Done sending DMs')

    @sendaccepteddm.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.sendaccepteddm <uni>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise
