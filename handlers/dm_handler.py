import discord
from discord.ext import commands
from services import dm_service, received_dms_service


class DmHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.type != discord.ChannelType.private or message.content.startswith('.'):
            return

        user_id = str(message.author.id)

        async with self.bot.db_conn.acquire() as connection:
            dm = dm_service.DMService(connection)
            received_dms = received_dms_service.ReceivedDMsService(connection)

            user_data_row = await self.bot.db_conn.fetchrow('SELECT user_id, dm_status, dm_programme FROM user_data '
                                                            'WHERE user_id = $1', user_id)

            if not user_data_row or user_data_row[1] is None:
                await received_dms.add_dm(user_id, message.content)
                return

            dm_status = user_data_row[1]
            dm_programme = user_data_row[2]

            result = False
            if dm_status == dm.DmStatus.AWAITING_RANK:
                result = await dm.handle_awaiting_rank(message, dm_programme)

            await received_dms.add_dm(user_id, message.content, result)


def setup(bot):
    bot.add_cog(DmHandler(bot))
