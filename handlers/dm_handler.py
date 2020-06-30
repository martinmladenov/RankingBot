import discord
from discord.ext import commands
from datetime import datetime
from utils import dm_util


class DmHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.type != discord.ChannelType.private or message.content.startswith('.'):
            return

        user_id = str(message.author.id)

        user_data_row = await self.bot.db_conn.fetchrow('SELECT user_id, dm_status, dm_programme FROM user_data '
                                                        'WHERE user_id = $1', user_id)

        if not user_data_row or user_data_row[1] is None:
            await self.save_received_dm(user_id, message.content, None)
            return

        dm_status = user_data_row[1]
        dm_programme = user_data_row[2]

        result = False
        if dm_status == dm_util.DmStatus.AWAITING_RANK:
            result = await dm_util.handle_awaiting_rank(message, dm_programme, self.bot.db_conn)

        await self.save_received_dm(user_id, message.content, result)

    async def save_received_dm(self, user_id: str, content: str, success):
        await self.bot.db_conn.execute(
            'INSERT INTO received_dms (user_id, message, success, timestamp) VALUES ($1, $2, $3, $4)',
            user_id, content, success, datetime.utcnow())


def setup(bot):
    bot.add_cog(DmHandler(bot))
