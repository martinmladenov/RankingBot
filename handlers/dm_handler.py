import discord
from discord.ext import commands
from services import dm_service, received_dms_service
import traceback


class DmHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.type != discord.ChannelType.private or message.content.startswith('.'):
            return

        async with (await self.bot.get_db_conn()).acquire() as connection:
            dm = dm_service.DMService(connection)
            received_dms = received_dms_service.ReceivedDMsService(connection)

            result = None
            try:
                result = await dm.handle_incoming_dm(message)
            except:
                traceback.print_exc()

            await received_dms.add_dm(str(message.author.id), message.content, result)


def setup(bot):
    bot.add_cog(DmHandler(bot))
