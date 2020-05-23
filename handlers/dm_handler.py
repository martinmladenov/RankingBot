import discord
from discord.ext import commands
from datetime import datetime
from database import db_fetchall, db_exec
from utils import dm_util


def save_received_dm(user_id: str, content: str, success):
    db_exec('INSERT INTO received_dms (user_id, message, success, timestamp) VALUES (%s, %s, %s, %s)',
            (user_id, content, success, datetime.utcnow()))


class DmHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.type != discord.ChannelType.private or message.content.startswith('.'):
            return

        user_id = message.author.id

        user_data_row = db_fetchall('SELECT user_id, dm_status, dm_programme FROM user_data WHERE user_id = %s',
                                    (str(user_id),))

        if not user_data_row or user_data_row[0][1] is None:
            save_received_dm(user_id, message.content, None)
            return

        dm_status = user_data_row[0][1]
        dm_programme = user_data_row[0][2]

        result = False
        if dm_status == dm_util.DmStatus.AWAITING_RANK:
            result = await dm_util.handle_awaiting_rank(message, dm_programme)

        save_received_dm(user_id, message.content, result)


def setup(bot):
    bot.add_cog(DmHandler(bot))
